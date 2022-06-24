import django

from delab.models import Tweet, TweetAuthor
from delab.tw_connection_util import DelabTwarc
from delab.network.DjangoTripleDAO import DjangoTripleDAO


def download_discussion_follower(conversation_id):
    dao = DjangoTripleDAO()
    discussion_tweets = Tweet.objects.filter(conversation_id=conversation_id).all()
    nodes = set()
    for discussion_tweet in discussion_tweets:
        # time.sleep(15)
        user = discussion_tweet.tw_author.twitter_id
        nodes.add(user)
    dao.add_discussion(nodes, conversation_id)
    user_ids = [discussion_tweet.tw_author.twitter_id for discussion_tweet in discussion_tweets]
    return user_ids


def download_followers_recursively(user_ids, n_level=1, following=False):
    twarc = DelabTwarc()
    download_followers(user_ids, twarc, n_level)


def persist_user(follower_data):
    try:
        TweetAuthor.objects.get_or_create(
            twitter_id=follower_data["id"],
            name=follower_data["name"],
            screen_name=follower_data["username"],
            location=follower_data.get("location", "unknown")
        )
    except django.db.utils.IntegrityError:
        pass


def download_followers(user_ids, twarc, n_level=1, following=False):
    dao = DjangoTripleDAO()
    follower_ids = []
    for user in user_ids:
        if following:
            followers = twarc.following(user=user, max_results=200)
            # followers = twarc.following(user=user, user_fields=["id", "name", "location", "username"])
        else:
            # followers = twarc.followers(user=user, user_fields=["id", "name", "location", "username"])
            followers = twarc.followers(user=user, max_results=200)
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
    n_level = n_level - 1
    if n_level > 0:
        download_followers(follower_ids, twarc, n_level=n_level)
