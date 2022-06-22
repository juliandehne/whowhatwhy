from delab.models import Tweet
from delab.tw_connection_util import DelabTwarc
from delab.network import Neo4jDAO as dao


def download_discussion_follower(conversation_id):
    discussion_tweets = Tweet.objects.filter(conversation_id=conversation_id).all()
    nodes = set()
    for discussion_tweet in discussion_tweets:
        # time.sleep(15)
        user = discussion_tweet.tw_author.twitter_id
        nodes.add(user)
    dao.add_discussion(nodes, conversation_id)
    user_ids = [discussion_tweet.tw_author.twitter_id for discussion_tweet in discussion_tweets]
    return user_ids


def download_followers_recursively(user_ids, n_level=1):
    twarc = DelabTwarc()
    download_followers(user_ids, twarc, n_level)


def download_followers(user_ids, twarc, n_level=1):
    follower_ids = []
    for user in user_ids:
        followers = twarc.following(user=user)
        for follower_iter in followers:
            # time.sleep(2)
            if "data" in follower_iter:
                follower_datas = follower_iter["data"]
                for follower_data in follower_datas:
                    follower = follower_data["id"]
                    follower_ids.append(follower)
                    dao.add_follower(follower, user)
    n_level = n_level - 1
    if n_level > 0:
        download_followers(follower_ids, twarc, n_level=n_level)
