from delab.models import Tweet
from delab.tw_connection_util import DelabTwarc


def run():
    discussion_tweets = Tweet.objects.filter(conversation_id=1504738179554983936).all()

    nodes = set()

    for discussion_tweet in discussion_tweets:

        user = discussion_tweet.tw_author_id
        nodes.add(user)

        # example for creating follower network from conversation
        twarc = DelabTwarc()
        followers = twarc.followers(user=user)

        edges = []

        pass
