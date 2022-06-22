from delab.models import Tweet
from delab.network import Neo4jDAO as dao
from delab.tw_connection_util import DelabTwarc

twarc = DelabTwarc()


def run():
    conversation_id = 1504738179554983936
    discussion_tweets = Tweet.objects.filter(conversation_id=conversation_id).all()

    nodes = set()

    for discussion_tweet in discussion_tweets:
        # time.sleep(15)
        user = discussion_tweet.tw_author.twitter_id
        nodes.add(user)

    dao.add_discussion(nodes, conversation_id)

    for discussion_tweet in discussion_tweets:
        user = discussion_tweet.tw_author.twitter_id
        followers = twarc.followers(user=user)
        for follower_iter in followers:
            # time.sleep(2)
            if "data" in follower_iter:
                follower_datas = follower_iter["data"]
                for follower_data in follower_datas:
                    follower = follower_data["id"]
                    dao.add_follower(follower, user)
                    #  nodes.add(follower)
                    # edges.append((follower, user))
