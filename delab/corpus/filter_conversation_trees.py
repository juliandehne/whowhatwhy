import networkx as nx
import pandas as pd
from django.forms.models import model_to_dict

from delab.TwConversationTree import TreeNode

from delab.corpus.filter_sequences import get_conversation_flows
from delab.models import Tweet, Conversation
from delab.network.conversation_network import get_nx_conversation_tree, get_root_author
from django_project.settings import MAX_CCCP_CONVERSATION_CANDIDATES


def get_conversation_trees(topic: str, conversation_id=None):
    """
    :param topic: the topic string
    :param conversation_id:  the conversation id
    :return:
    """
    return convert_to_conversation_trees(conversation_id, topic)


def convert_to_conversation_trees(conversation_id=None, topic=None):
    """

    @param conversation_id: the id of the conversation
    @param topic: the topic title as string
    @return: a dictionary in the form {conversation_id : int  -> rootNode : TreeNode}
    """
    objects = Tweet.objects.select_related("tw_author")

    if conversation_id is not None:
        if topic is not None:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True,
                                              conversation_id=conversation_id,
                                              topic__title=topic).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False,
                                                  topic__title=topic,
                                                  conversation_id=conversation_id).order_by('-created_at').all()]
        else:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True,
                                              conversation_id=conversation_id).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False,
                                                  conversation_id=conversation_id).order_by('-created_at').all()]
    else:
        if topic is not None:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True,
                                              topic__title=topic).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False,
                                                  topic__title=topic).order_by('-created_at').all()]
        else:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False).order_by('-created_at').all()]
    return reconstruct_trees_from_records(not_roots_as_record, roots_as_record)


def author_tweet_to_records(tweet):
    result = model_to_dict(tweet)
    if tweet.tw_author is not None:
        result.update({"tw_author__name": tweet.tw_author.name})
        result.update({"tw_author__location": tweet.tw_author.location})
    else:
        result.update({"author_name": "unknown"})
    return result


def reconstruct_trees_from_records(not_roots_as_rec, roots_as_rec):
    trees_roots = {}
    not_roots = {}
    for root_data in roots_as_rec:
        root_node = TreeNode(root_data, root_data["twitter_id"], root_data["tn_parent"])
        trees_roots[root_data["conversation_id"]] = root_node
    # group tree elements based on their conversation id
    conversation_ids = set()
    for not_root in not_roots_as_rec:
        conversation_id = not_root["conversation_id"]
        conversation_ids.add(conversation_id)
        if conversation_id not in not_roots:
            not_roots[conversation_id] = [not_root]
        else:
            not_roots[conversation_id] = not_roots.get(conversation_id) + [not_root]
    for conversation_id in conversation_ids:
        if conversation_id in trees_roots:
            tree_node = trees_roots.get(conversation_id)
            orphans = []
            for not_root in not_roots[conversation_id]:
                to_add_node = TreeNode(not_root, not_root["twitter_id"], not_root["tn_parent"])
                orphans.append(to_add_node)
            # now solve all the orphans that have not been seen
            orphan_added = True
            while orphan_added:
                orphan_added, orphans = solve_orphans(orphans, tree_node)
            trees_roots[conversation_id] = tree_node
    return trees_roots


def solve_orphans(orphans, tree_node):
    if len(orphans) == 0:
        return False, []

    rest_orphans = []
    orphan_added = False
    for orphan in orphans:
        added = tree_node.find_parent_of(orphan)
        # either or the list es reduced by one element
        if not added:
            rest_orphans.append(orphan)
        # either nothing was found that False is returned stopping the cycle
        else:
            orphan_added = True
    if len(orphans) == len(rest_orphans):
        # print(f"could not reconstruct faulty tree for conversation_id {orphans[0].data['conversation_id']}")
        # print("could not reconstruct faulty tree with {} orphans ".format(rest_orphans))
        return False, rest_orphans
    assert len(orphans) != len(rest_orphans)
    return orphan_added, rest_orphans


def get_conversation_root_as_data(conversation_id):
    tweet = Tweet.objects.filter(conversation_id=conversation_id, tn_parent__isnull=True).get()
    result = {"text": tweet.text, "created_at": tweet.created_at, "id": tweet.twitter_id, "author_id": tweet.author_id,
              "conversation_id": tweet.conversation_id, "lang": tweet.language}
    return result


def get_well_structured_conversation_ids(n=-1, n_conversation_candidates=MAX_CCCP_CONVERSATION_CANDIDATES):
    """
    computes the n discussions with the best set of properties in terms of a useful dialogue or interaction
    This specifically filters out mushroom structures (with a root and many replies) or those reply trees, that
    have short conversation flows (depth) or are dominated by single users (mostly the root user)
    @param n_conversation_candidates:
    @param n:
    @return:
    """
    qs = Conversation.objects.all()[:n_conversation_candidates]
    q = qs.values('conversation_id', 'depth', 'branching_factor', 'root_dominance')
    df = pd.DataFrame.from_records(q)

    df_normalized = df.drop("conversation_id", axis=1)
    df_normalized = (df_normalized - df_normalized.mean()) / df_normalized.std()
    df_normalized["branching_factor"] *= -1
    df_normalized["root_dominance"] *= -1
    df_normalized["metrics_avg"] = df_normalized["branching_factor"] + df_normalized["root_dominance"] + df_normalized[
        "depth"]
    df_normalized["conversation_id"] = df.conversation_id
    # print(df_normalized.head(2))
    df_normalized.sort_values("metrics_avg", inplace=True)
    if n > 0:
        result = df_normalized.head(n)
    else:
        result = df_normalized
    return result.conversation_id


def compute_conversation_properties(conversation_ids):
    """
    computes properties like the depth or the branching factor for all conversations in order to be used later on
    as a filter for conversations that come close to a useful discussion/discourse
    @param conversation_ids:
    """
    created_count = 0
    for conversation_id in conversation_ids:
        try:
            if Tweet.objects.filter(conversation_id=conversation_id).count() > 5000:
                continue
            print(conversation_id)
            print("computed {} of {} conversation filters".format(created_count, len(conversation_ids)))
            reply_tree = get_nx_conversation_tree(conversation_id)
            branching_factor = nx.tree.branching_weight(reply_tree)

            root_node_author_id = get_root_author(conversation_id)
            root_tweet_count = Tweet.objects.filter(conversation_id=conversation_id,
                                                    tw_author__id=root_node_author_id).count()
            not_root_tweet_count = Tweet.objects.filter(conversation_id=conversation_id).exclude(
                tw_author__id=root_node_author_id).count()
            root_dominance = root_tweet_count / (not_root_tweet_count + 1)

            flow_dict, longest_name = get_conversation_flows(conversation_id)
            depth = len(flow_dict[longest_name])

            created = False
            try:
                conversation, created = Conversation.objects.get_or_create(
                    conversation_id=conversation_id,
                    branching_factor=branching_factor,
                    root_dominance=root_dominance,
                    depth=depth
                )
            except Exception as integrity_error:
                print(integrity_error)

            if created:
                created_count += 1

            print("created {}  conversations ".format(created_count))
        except AssertionError as ae:
            print(ae)
