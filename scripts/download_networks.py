import networkx as nx

from delab.models import Tweet
from delab.tw_connection_util import DelabTwarc


def run():
    discussion_tweets = Tweet.objects.filter(conversation_id=1504738179554983936).all()

    nodes = set()
    edges = []

    for discussion_tweet in discussion_tweets:

        user = discussion_tweet.tw_author.twitter_id
        nodes.add(user)

        # example for creating follower network from conversation
        twarc = DelabTwarc()
        followers = twarc.followers(user=user)
        for follower_iter in followers:
            if "data" in follower_iter:
                follower_datas = follower_iter["data"]
                for follower_data in follower_datas:
                    follower = follower_data["id"]
                    nodes.add(follower)
                    edges.append((follower, user))

    G = nx.Graph()
    # G.add_node(1)
    G.add_nodes_from(list(nodes))
    G.add_edges_from(edges)
    nx.draw(G)

