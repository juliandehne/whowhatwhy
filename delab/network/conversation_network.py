import logging
from time import sleep

import django
import networkx as nx

from delab.corpus.download_author_information import download_authors
from delab.models import Tweet, TweetAuthor
from delab.tw_connection_util import DelabTwarc
from util.abusing_lists import batch

logger = logging.getLogger(__name__)


def get_participants(conversation_id):
    dao = DjangoTripleDAO()
    discussion_tweets = Tweet.objects.filter(conversation_id=conversation_id).all()
    nodes = set()
    for discussion_tweet in discussion_tweets:
        # time.sleep(15)
        user = discussion_tweet.author_id
        nodes.add(user)
    dao.add_discussion(nodes, conversation_id)  # this would be need in case of neo4j
    return nodes


def download_followers_recursively(user_ids, n_level=1, following=False):
    twarc = DelabTwarc()
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
                followers = twarc.following(user=user, user_fields="id,name,location,username", max_results=500)
            else:
                followers = twarc.followers(user=user, user_fields="id,name,location,username", max_results=500)
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
        # one batch finished
        logger.debug(
            "Going to sleep after downloading following for 15 user, {}/{} user finished".format(count, len(user_ids)))
        sleep(15 * 60)

    n_level = n_level - 1
    if n_level > 0:
        download_followers(follower_ids, twarc, n_level=n_level)


def download_missing_author_data(user_ids):
    missing_authors = []
    for user_id in user_ids:
        if not TweetAuthor.objects.filter(twitter_id=user_id).exists():
            missing_authors.append(user_id)
    download_authors(missing_authors)


def get_nx_conversation_graph(conversation_id):
    replies = Tweet.objects.filter(conversation_id=conversation_id).only("id", "twitter_id", "tn_parent_id")
    G = nx.DiGraph()
    edges = []
    nodes = []
    for row in replies:
        nodes.append(row.twitter_id)
        G.add_node(row.twitter_id, id=row.id)
        if row.tn_parent_id is not None:
            edges.append((row.tn_parent_id, row.twitter_id))
    G.add_edges_from(edges)
    return G
