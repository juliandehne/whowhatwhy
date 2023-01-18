import logging
from itertools import combinations
from time import sleep

import django
import matplotlib.pyplot as plt
import networkx as nx
from django.db.models import Exists, OuterRef
from networkx.drawing.nx_pydot import graphviz_layout

from delab.corpus.download_author_information import download_authors
from delab.delab_enums import PLATFORM
from delab.models import Tweet, TweetAuthor, FollowerNetwork, Mentions
from delab.network.DjangoTripleDAO import DjangoTripleDAO
from delab.tw_connection_util import DelabTwarc
from django_project.settings import performance_conversation_max_size
from util.abusing_lists import batch

logger = logging.getLogger(__name__)


class GRAPH:
    class ATTRIBUTES:
        CREATED_AT = "created_at"

    class LABELS:
        MENTIONS = "mentions"
        PARENT_OF = "parent_of"
        AUTHOR_OF = "author_of"

    class SUBSETS:
        TWEETS = "tweets"
        AUTHORS = "authors"


def download_twitter_follower(levels, n_conversations=-1):
    count = 0
    conversation_ids = set(Tweet.objects.filter(platform=PLATFORM.TWITTER).values_list('conversation_id', flat=True))
    # conversation_ids = prevent_multiple_downloads(conversation_ids)
    conversation_ids = restrict_conversations_to_reasonable(conversation_ids)
    if len(conversation_ids) > n_conversations > 0:
        conversation_ids = list(conversation_ids)[:n_conversations]
        for conversation_id in conversation_ids:
            count += 1
            download_conversation_network(conversation_id, conversation_ids, count, levels)
    else:
        if len(conversation_ids) < n_conversations > 0:
            for conversation_id in conversation_ids:
                count += 1
                download_conversation_network(conversation_id, conversation_ids, count, levels)
        else:
            for conversation_id in conversation_ids:
                count += 1
                download_conversation_network(conversation_id, conversation_ids, count, levels)
    logger.info("finished downloading networks")


def get_participants(conversation_id, filter_follower_not_downloaded=False, filter_following_not_downloaded=False):
    """
    as a side effect this would create a conversation node in neo4j
    :param filter_following_not_downloaded:
    :param filter_follower_not_downloaded:
    :param conversation_id:
    :return:
    """
    dao = DjangoTripleDAO()
    if filter_following_not_downloaded:
        discussion_tweets = Tweet.objects.filter(conversation_id=conversation_id,
                                                 tw_author__following_downloaded=False).all()
    else:
        if filter_follower_not_downloaded:
            discussion_tweets = Tweet.objects.filter(conversation_id=conversation_id,
                                                     tw_author__follower_downloaded=False).all()
        else:
            discussion_tweets = Tweet.objects.filter(conversation_id=conversation_id).all()

    nodes = set()
    for discussion_tweet in discussion_tweets:
        # time.sleep(15)
        user = discussion_tweet.author_id
        nodes.add(user)
    dao.add_discussion(nodes, conversation_id)  # this would be need in case of neo4j
    return nodes


def download_followers_recursively(user_ids, twarc, n_level=1, following=False):
    download_followers(user_ids, twarc, n_level, following)


def persist_user(follower_data):
    try:
        author, created = TweetAuthor.objects.get_or_create(
            twitter_id=follower_data["id"],
            name=follower_data["name"],
            screen_name=follower_data["username"],
            location=follower_data.get("location", "unknown")
        )
    except django.db.utils.IntegrityError as ex:
        # logger.error(ex)
        pass
    except Exception as e:
        logger.error(e)


def download_followers(user_ids, twarc, n_level=1, following=False):
    download_missing_author_data(user_ids)
    dao = DjangoTripleDAO()
    follower_ids = []
    count = 0
    user_batches = batch(list(user_ids), 15)
    for user_batch in user_batches:
        for user in user_batch:
            count += 1
            # try:
            if following:
                followers = twarc.following(user=user, user_fields="id,name,location,username", max_results=100)
            else:
                followers = twarc.followers(user=user, user_fields="id,name,location,username", max_results=10)
            for follower_iter in followers:
                # time.sleep(2)
                if "data" in follower_iter:
                    follower_datas = follower_iter["data"]
                    for follower_data in follower_datas:
                        persist_user(follower_data)
                        follower = follower_data["id"]
                        follower_ids.append(follower)
                        if follower:
                            dao.add_follower(user, follower)
                        else:
                            dao.add_follower(follower, user)
                break  # we don't want users with huge follower numbers to dominate the network anyways
        # one batch finished
        logger.debug(
            "Going to sleep after downloading following for max 15 user, {}/{} user finished".format(count,
                                                                                                     len(user_ids)))
        sleep(15 * 60)

    # update author fields
    if following:
        TweetAuthor.objects.filter(twitter_id__in=user_ids).update(following_downloaded=True)
    else:
        TweetAuthor.objects.filter(twitter_id__in=user_ids).update(follower_downloaded=True)

    n_level = n_level - 1
    if n_level > 0:
        download_followers(follower_ids, twarc, n_level=n_level)


def download_missing_author_data(user_ids):
    missing_authors = []
    for user_id in user_ids:
        if not TweetAuthor.objects.filter(twitter_id=user_id).exists():
            missing_authors.append(user_id)
    download_authors(missing_authors)


class FaultyGraphException(Exception):
    pass


def compute_subsequent_merge(conversation_id):
    """
    @param conversation_id:
    @return: [to eliminate nodes for merge], {node_id -> new_parent}
    """
    tweets = Tweet.objects.filter(conversation_id=conversation_id).order_by("created_at")
    to_delete_list = []
    to_change_map = {}
    for tweet in tweets:
        # if tweet.twitter_id == 82814624:
        #    print("testing 1")

        # we are not touching the root
        if tweet.tn_parent is None:
            continue
        # if a tweet is merged, ignore
        if tweet.twitter_id in to_delete_list:
            continue
        # if a tweet shares the author with its parent, deleted it
        if tweet.author_id == tweet.tn_parent.author_id:
            to_delete_list.append(tweet.twitter_id)
        # if the parent has been deleted, find the next available parent
        else:
            current = tweet
            while current.tn_parent.twitter_id in to_delete_list:
                # we can make this assertion because we did not delete the root
                assert current.tn_parent is not None
                current = current.tn_parent
            if current.twitter_id != tweet.twitter_id:
                to_change_map[tweet.twitter_id] = current.tn_parent.twitter_id

    return to_delete_list, to_change_map


def get_nx_conversation_graph(conversation_id, merge_subsequent=False):
    to_eliminate_nodes = []
    changed_nodes = {}
    if merge_subsequent is True:
        to_eliminate_nodes, changed_nodes = compute_subsequent_merge(conversation_id)
    replies = Tweet.objects.filter(conversation_id=conversation_id)
    # .only("id", "twitter_id", "tn_parent_id", "created_at")

    G = nx.DiGraph()
    edges = []
    nodes = [reply.twitter_id for reply in replies if reply.twitter_id not in to_eliminate_nodes]
    for row in replies:
        if row.twitter_id not in to_eliminate_nodes:
            nodes.append(row.twitter_id)
            G.add_node(row.twitter_id, id=row.id, created_at=row.created_at)
            if row.tn_parent_id is not None:
                if row.tn_parent_id not in nodes:
                    logger.error("conversation {} has no root_node".format(conversation_id))
                assert row.tn_parent_id in nodes
                if row.twitter_id in changed_nodes:
                    new_parent = changed_nodes[row.twitter_id]
                    if new_parent is not None:
                        edges.append((new_parent, row.twitter_id))
                    else:
                        G.remove_node(row.twitter_id)
                else:
                    edges.append((row.tn_parent_id, row.twitter_id))
    assert len(edges) > 0, "there are no edges for conversation {}".format(conversation_id)
    G.add_edges_from(edges)
    if merge_subsequent:
        return G, to_eliminate_nodes, changed_nodes
    return G


def get_root(conversation_graph: nx.DiGraph):  # tree rooted at 0
    roots = [n for n, d in conversation_graph.in_degree() if d == 0]
    return roots[0]


def get_root_author(conversation_id):
    return Tweet.objects.filter(tn_parent__isnull=True, conversation_id=conversation_id).get().tw_author_id


def get_nx_conversation_tree(conversation_id, merge_subsequent=False):
    g = get_nx_conversation_graph(conversation_id, merge_subsequent=merge_subsequent)
    root = get_root(g)
    tree = nx.bfs_tree(g, root)
    return tree


def get_mention_graph(conversation_id):
    g = compute_author_graph(conversation_id=conversation_id)
    mentions = Mentions.objects.filter(conversation_id=conversation_id).all()
    for mention in mentions:
        author = mention.tweet.author_id
        g.add_edge(author, mention.mentionee_id, label=GRAPH.LABELS.MENTIONS)
    return g


def get_tweet_subgraph(conversation_graph):
    nodes = (
        node
        for node, data
        in conversation_graph.nodes(data=True)
        if data.get("subset") == "tweets"
    )
    subgraph = conversation_graph.subgraph(nodes)
    return subgraph


def compute_author_graph(conversation_id: int):
    """
    computes the combined reply tree and author tree (author - parent_of -> tweet)
    @param conversation_id:
    @return:
    """
    G = get_nx_conversation_graph(conversation_id)
    G2 = compute_author_graph_helper(G, conversation_id)
    return G2


def compute_author_graph_helper(G, conversation_id):
    author_tweet_pairs = Tweet.objects.filter(conversation_id=conversation_id).only("twitter_id", "author_id")
    G2 = nx.MultiDiGraph()
    G2.add_nodes_from(G.nodes(data=True), subset="tweets")
    G2.add_edges_from(G.edges(data=True), label="parent_of")
    for result_pair in author_tweet_pairs:
        G2.add_node(result_pair.author_id, author=result_pair.author_id, subset="authors")
        G2.add_edge(result_pair.author_id, result_pair.twitter_id, label=GRAPH.LABELS.AUTHOR_OF)
    return G2


def compute_author_interaction_graph(conversation_id):
    author_ids = set(Tweet.objects.filter(conversation_id=conversation_id).values_list("author_id", flat=True).all())
    # author_ids = [str(a) for a in author_ids]
    G = compute_author_graph(conversation_id)
    # author_graph_network = nx.projected_graph(G, author_ids)

    G2 = nx.DiGraph()
    G2.add_nodes_from(author_ids)

    # author_pairs = combinations(author_ids, 2)
    for a in author_ids:
        tw1_out_edges = G.out_edges(a, data=True)
        for _, tw1, out_attr in tw1_out_edges:
            tw2_out_edges = G.out_edges(tw1, data=True)
            for _, tw2, _ in tw2_out_edges:
                in_edges = G.in_edges(tw2, data=True)
                # since target already has a source, there can only be in-edges of type author_of
                for reply_author, _, in_attr in in_edges:
                    if in_attr["label"] == GRAPH.LABELS.AUTHOR_OF:
                        assert reply_author in author_ids
                        if a != reply_author:
                            G2.add_edge(a, reply_author)

    return G2


def restrict_conversations_to_reasonable(unhandled_conversation_ids):
    reasonable_small_conversations = []
    for conversation_id in unhandled_conversation_ids:
        if TweetAuthor.objects.filter(tweet__in=Tweet.objects.filter(conversation_id=conversation_id)).count() \
                <= performance_conversation_max_size:
            reasonable_small_conversations.append(conversation_id)
    return reasonable_small_conversations


def download_conversation_network(conversation_id, conversation_ids, count, levels):
    twarc = DelabTwarc()
    user_ids = get_participants(conversation_id, filter_following_not_downloaded=True)
    download_followers_recursively(user_ids, twarc, levels, following=True)
    # this would also search the network in the other direction
    user_ids = get_participants(conversation_id, filter_follower_not_downloaded=True)
    download_followers_recursively(user_ids, twarc, levels, following=False)
    # logger.debug(" {}/{} conversations finished".format(count, len(conversation_ids)))


def prevent_multiple_downloads(conversation_ids):
    unhandled_conversation_ids = []
    for conversation_id in conversation_ids:
        authors_is = set(Tweet.objects.filter(conversation_id=conversation_id).values_list("author_id", flat=True))
        author_part_of_networks = TweetAuthor.objects.filter(twitter_id__in=authors_is). \
            filter(Exists(FollowerNetwork.objects.filter(source_id=OuterRef('pk')))
                   | Exists(FollowerNetwork.objects.filter(target_id=OuterRef('pk')))).distinct()
        assert len(authors_is) > 0
        if not len(author_part_of_networks) > len(authors_is) / 2:
            unhandled_conversation_ids.append(conversation_id)
        else:
            logger.debug("conversation {} has been handled before".format(conversation_id))
    return unhandled_conversation_ids


def draw_author_conversation_dist(conversation_id):
    reply_graph = get_nx_conversation_graph(conversation_id)
    conversation_graph = compute_author_graph(conversation_id)
    root_node = get_root(reply_graph)
    paint_bipartite_author_graph(conversation_graph, root_node=root_node)


def paint_bipartite_author_graph(G2, root_node):
    # Specify the edges you want here
    red_edges = [(source, target, attr) for source, target, attr in G2.edges(data=True) if
                 attr['label'] == GRAPH.LABELS.AUTHOR_OF]
    # edge_colours = ['black' if edge not in red_edges else 'red'
    #                for edge in G2.edges()]
    black_edges = [edge for edge in G2.edges(data=True) if edge not in red_edges]
    # Need to create a layout when doing
    # separate calls to draw nodes and edges
    paint_bipartite(G2, black_edges, red_edges, root_node=root_node)


def paint_bipartite(G2, black_edges, red_edges, root_node):
    # pos = nx.multipartite_layout(G2)

    pos = graphviz_layout(G2, prog="twopi", root=root_node)
    nx.draw_networkx_nodes(G2, pos, node_size=400)
    nx.draw_networkx_labels(G2, pos)
    nx.draw_networkx_edges(G2, pos, edgelist=red_edges, edge_color='red', arrows=True)
    nx.draw_networkx_edges(G2, pos, edgelist=black_edges, arrows=True)
    plt.show()


def paint_reply_graph(conversation_graph: nx.DiGraph):
    assert nx.is_tree(conversation_graph)
    root = get_root(conversation_graph)
    tree = nx.bfs_tree(conversation_graph, root)
    pos = graphviz_layout(tree, prog="twopi")
    # add_attributes_to_plot(conversation_graph, pos, tree)
    nx.draw_networkx_labels(tree, pos)
    nx.draw(tree, pos)
    plt.show()


def add_attributes_to_plot(conversation_graph, pos, tree):
    labels = dict()
    names = nx.get_node_attributes(conversation_graph, GRAPH.ATTRIBUTES.CREATED_AT)
    for node in conversation_graph.nodes:
        labels[node] = f"{names[node]}\n{node}"
    nx.draw_networkx_labels(tree, labels=labels, pos=pos)
