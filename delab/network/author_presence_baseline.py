"""
the idea here is to establish a baseline what to measure the author presence measures against.
- a simple probability distribution of having seen a tweet based on reply distance and root distance
- both reply and root distance prob should start with 1 and decrease by half each step, vision prob is the means between
  the two measurements. Experiment with an alpha between 0.1 and 0.3 that is distracted from the original root distance score (1)
- not sure about the time delta influence (or whether it should be included),
    maybe normalize time delta and multiply it given factor beta. Choose beta so that it does not change the order of
    reply or root hierarchy influences
"""
import networkx as nx

from delab.models import Tweet
from delab.network.author_presence import prepare_row_analysis, compute_timedelta_feature, compute_follower_features


def calculate_baseline_row(tweet: Tweet, reply_graph: nx.DiGraph, follower_graph: nx.MultiDiGraph,
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
            compute_baseline_reply_features(path_dict, current_node_id, result, row_node_id, conversation_depth)
            compute_timedelta_feature(current_node_timestamp, result, tweet)
            compute_baseline_root_distance_feature(root_path_dict, current_node_id, result, root_node, row_node_id,
                                                   conversation_depth)
            result["current"] = tweet.twitter_id
            result["beam_node"] = current_node_id
            compute_follower_features(conversation_graph, current_node_id, follower_graph, result,
                                      row_node_author_id, conversation_id=tweet.conversation_id)
            result["platform"] = tweet.platform
            result["conversation_id"] = tweet.conversation_id
        if result:
            result_of_results.append(result)

    return result_of_results


def compute_baseline_reply_features(path_dict, current_node_id, result, row_node_id, conversation_depth):
    """
    this computes the distance of the two tweets based on how many replies stand between them in the tree
    :param path_dict:
    :param current_node_id:
    :param result:
    :return:
    """
    assert current_node_id != row_node_id
    weight = 1.0
    path_found = False
    for i in range(1, conversation_depth):
        path_exists = (current_node_id, i) in path_dict
        path_found = path_found or path_exists
        result_value = 0
        if path_exists:
            result_value = 1
        result["reply_distance_" + str(i)] = result_value * weight
        weight = 0.5 * weight


def compute_baseline_root_distance_feature(path_dict, current_node_id, result, root_node, row_node_id,
                                           conversation_depth):
    result["root_distance_0"] = 0
    if root_node == current_node_id:
        result["root_distance_0"] = 1

    weight = 1
    path_found = False
    for i in range(1, conversation_depth):
        path_exists = (current_node_id, i) in path_dict
        result_value = 0
        path_found = path_found or path_exists
        if path_exists:
            result_value = 1
        result["root_distance_" + str(i)] = result_value
        weight = weight * 0.25  # instead of this decay weighing the importance based on PA might be interesting
    assert (not path_found) or root_node != current_node_id

