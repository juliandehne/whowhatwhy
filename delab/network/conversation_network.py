import logging
from time import sleep

import django

from delab.models import Tweet, TweetAuthor
from delab.network.DjangoTripleDAO import DjangoTripleDAO
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
        TweetAuthor.objects.get_or_create(
            twitter_id=follower_data["id"],
            name=follower_data["name"],
            screen_name=follower_data["username"],
            location=follower_data.get("location", "unknown")
        )
    except django.db.utils.IntegrityError as ex:
        logger.error(ex)


def download_followers(user_ids, twarc, n_level=1, following=False):
    dao = DjangoTripleDAO()
    follower_ids = []
    count = 0
    user_batches = batch(list(user_ids), 15)
    for user_batch in user_batches:
        for user in user_batch:
            count += 1
            try:
                if following:
                    followers = twarc.following(user=user, user_fields="id,name,location,username", max_results=500)
                    # followers = twarc.following(user=user, user_fields=["id", "name", "location", "username"])
                else:
                    # followers = twarc.followers(user=user, user_fields=["id", "name", "location", "username"])
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
            except Exception as e:
                logger.error(e)
                logger.error("something went wrong with downloading the network")
        # one batch finished
        logger.debug(
            "Going to sleep after downloading following for 15 user, {}/{} user finished".format(count, len(user_ids)))
        sleep(15 * 60)

    n_level = n_level - 1
    if n_level > 0:
        download_followers(follower_ids, twarc, n_level=n_level)
