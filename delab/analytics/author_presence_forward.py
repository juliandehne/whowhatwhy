import logging

import networkx as nx

from delab.models import Tweet
from delab.analytics.author_presence import prepare_row_analysis, compute_reply_features, compute_timedelta_feature, \
    compute_root_distance_feature, compute_follower_features

logger = logging.getLogger(__name__)

"""
the same idea as the author presence but now the current tweet is also the beam node
- it is a multi class classification problem with the different authors as the classes, y is 1 if it is the author to be classified to have vision of
- sample is the tree structure of the whole reply tree (a author answering one or two later may still be informative) of having seen the tweet

"""


def compute_forward_y(conversation_graph, current_node_id, result, tweet):
    pass


def calculate_forward_row(tweet: Tweet, reply_graph: nx.DiGraph, follower_graph: nx.MultiDiGraph,
                          conversation_graph: nx.MultiDiGraph, root_node: int):
    """

    :param root_node:
    :param reply_graph:
    :param conversation_graph: directed graph that represents the conversation tree, node ids are twitter ids
    :param follower_graph: directed graph that represents the follower structures, node ids are the author ids
    :param tweet:
    :return: a dictionary of the tweet history containing the column names as keys and the features as values
    """

    conversation_depth, path_dict, reply_nodes, result_of_results, root_path_dict, row_node_author_id, row_node_id = \
        prepare_row_analysis(conversation_graph, reply_graph, root_node, tweet)

    for current_node_id, current_node_attr in reply_nodes:
        result = {}
        current_node_timestamp = current_node_attr["created_at"]

        if row_node_id != current_node_id:
            compute_reply_features(path_dict, current_node_id, result, row_node_id, conversation_depth)
            compute_timedelta_feature(current_node_timestamp, result, tweet)
            compute_root_distance_feature(root_path_dict, current_node_id, result, root_node, row_node_id,
                                          conversation_depth)
            compute_forward_y(conversation_graph, current_node_id, result, tweet)
            result["current"] = tweet.twitter_id
            result["beam_node"] = current_node_id
            compute_follower_features(conversation_graph, current_node_id, follower_graph, result,
                                      row_node_author_id, conversation_id=tweet.conversation_id)
            result["platform"] = tweet.platform
            result["conversation_id"] = tweet.conversation_id
            result["author"] = tweet.author_id
            result["current_time"] = tweet.created_at
            result["beam_node_time"] = current_node_timestamp
            compute_previous_posts_feature(conversation_graph, current_node_id, result, tweet)

        if result:
            result_of_results.append(result)

    return result_of_results


def compute_previous_posts_feature(conversation_graph, current_node_id, result, tweet):
    in_edges = conversation_graph.in_edges(current_node_id)
    for source, target in in_edges:
        if source == tweet.author_id:
            all_path = nx.all_simple_paths(conversation_graph, current_node_id, tweet.twitter_id)
            for path in all_path:
                result["same_author_path_{}".format(len(path) - 1)] = 1

