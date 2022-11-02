import math

import matplotlib.pyplot as plt
import networkx as nx

from delab.models import Tweet
from delab.network.conversation_network import get_nx_conversation_graph, get_root


def author_centrality(conversation_id):
    """
    :param conversation_id: the id of the conversation
    :return: a list of dictionaries in the form of
     [{author:"author":author_id, "centrality_score":score_value, "conversation_id": conversation_id}]
    the key "root_distance_avg" holds the average distance to the root node for the given author
    """
    tweets = list(Tweet.objects.filter(conversation_id=conversation_id).all())

    reply_graph, to_eliminate_nodes, changed_nodes = get_nx_conversation_graph(conversation_id, merge_subsequent=True)
    # nx.draw(reply_graph)
    # plt.show()
    # unlinked_nodes = [node for node in reply_graph.nodes() if reply_graph.in_degree(node) == 0]
    # print(unlinked_nodes)

    # longest_path = nx.dag_longest_path(reply_graph)
    tweets_2 = [tweet for tweet in tweets if tweet.twitter_id not in to_eliminate_nodes]
    if len(to_eliminate_nodes) > 0:
        assert len(tweets_2) < len(tweets)
    root_node = get_root(reply_graph)

    conversation_paths = []
    for node in reply_graph:
        if reply_graph.out_degree(node) == 0:  # it's a leaf
            conversation_paths.append(nx.shortest_path(reply_graph, root_node, node))

    records = compute_conversation_author_centrality(conversation_id, conversation_paths, reply_graph, root_node,
                                                     tweets_2)
    return records


def compute_conversation_author_centrality(conversation_id, conversation_paths, reply_graph, root_node, tweets):
    records = []
    tweet2author_dict = {}
    tweet2platform_dict = {}
    for tweet in tweets:
        tweet2platform_dict[tweet.twitter_id] = tweet.platform
        tweet2author_dict[tweet.twitter_id] = tweet.author_id

    for key, value in tweet2author_dict.items():
        record = {}
        author_score = {}
        root_distance_sum = {}
        path_counts = 0
        for path in conversation_paths:
            if key in path:
                path_counts += 1
                path_score = compute_centrality_bias(path, key)
                current_author_score = author_score.get(value, 0)
                author_score[value] = current_author_score + path_score
                root_distance = len(nx.shortest_path(reply_graph, root_node, key))
                current_root_distance = root_distance_sum.get(value, 0)
                root_distance_sum[value] = current_root_distance + root_distance
        record["author"] = value
        record["centrality_score"] = author_score[value]
        record["conversation_id"] = conversation_id
        record["platform"] = tweet2platform_dict[key]
        record["root_distance_avg"] = root_distance_sum[value] / path_counts
        records.append(record)
    return records


def compute_centrality_bias(path, node):
    i = path.index(node) + 1
    centrality = math.ceil(len(path) / 2)
    node_centrality = abs(centrality - i) / (len(path) - 1)
    node_centrality_to_1 = 1 - node_centrality
    return node_centrality_to_1
