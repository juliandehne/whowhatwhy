import networkx as nx
from networkx import NetworkXNoCycle

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet


def run():
    # validate foreign keys exist
    # validate_foreign_keys()

    validate_cycles()


def validate_cycles():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        validate_conversation_tree(conversation_id)


def validate_conversation_tree(conversation_id):
    nodes = set()
    edges = []
    tweets = Tweet.objects.filter(conversation_id=conversation_id).all()
    for tweet in tweets:
        nodes.add(tweet.twitter_id)
        if tweet.tn_parent_id is not None:
            nodes.add(tweet.tn_parent_id)
            edges.append((tweet.twitter_id, tweet.tn_parent_id))
    G = nx.Graph()
    # G.add_node(1)
    G.add_nodes_from(list(nodes))
    G.add_edges_from(edges)
    try:
        cycles = list(nx.find_cycle(G, orientation="ignore"))
        if len(cycles) > 0:
            raise Exception("there are cycles")
    except NetworkXNoCycle:
        pass


def validate_foreign_keys():
    tweets = Tweet.objects
    twitter_ids = list(tweets.values_list("twitter_id", flat=True))
    for tweet in tweets.all():
        if tweet.tn_parent_id not in twitter_ids and tweet.tn_parent_id is not None:
            # print(tweet.conversation_id)
            print(tweet.tn_parent_id)
