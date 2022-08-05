"""
The basic idea:
- vision of a graph is defined as an author having a high probability of having seen a random tweet when he was writing!
- P(tweet seen | reply) is 1for a tweet the author replied to
- Note: all the following params might need to be trained with a classifierort
- P(tweet seen | replied to) is 0.8 that mentions the author or replies directly to a tweet of the author
- P(tweet seen | reply of reply) is  1/2 * P(tweet seen | reply)
- P(tweet seen | replied to of replied to) is  1/4 * P(tweet seen | replied_to)
- P(tweet seen | following_author) is 0.9
- P(tweet seen | following_author that follows author) is 1/5 * P(tweet seen | following_author)
  Note 2:  P(answer | tweet seen) should integrate alpha where alpha is computed based on the time that has passed in average when answering tweetss

  https://towardsdatascience.com/build-a-simple-neural-network-using-pytorch-38c55158028d

  Read probability and answer probability can be viewed as dependent. You can only write if you have read + some sort of interest in answering.
  P(W | R and I) = P(R) + p(I)
"""
import logging

import networkx as nx
import networkx.exception

from delab.models import Tweet
from delab.network.conversation_network import get_root

logger = logging.getLogger(__name__)


def calculate_row(tweet: Tweet, reply_graph: nx.DiGraph, follower_graph: nx.MultiDiGraph,
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
            compute_y(conversation_graph, current_node_id, result, tweet)
            result["current"] = tweet.twitter_id
            result["beam_node"] = current_node_id
            compute_follower_features(conversation_graph, current_node_id, follower_graph, result,
                                      row_node_author_id, conversation_id=tweet.conversation_id)
            result["platform"] = tweet.platform
            result["conversation_id"] = tweet.conversation_id

        if result:
            result_of_results.append(result)

    return result_of_results


def prepare_row_analysis(conversation_graph, reply_graph, root_node, tweet):
    result_of_results = []
    row_node_id = tweet.twitter_id
    row_node_author_id = tweet.author_id
    # we are only looking at the picture before the current tweet
    reply_nodes = [(x, y) for x, y in conversation_graph.nodes(data=True)
                   if y['subset'] == "tweets" and y['created_at'] < tweet.created_at]
    conversation_depth = nx.dag_longest_path_length(reply_graph)
    # call the all simple graphs is too slow
    path_dict = compute_all_path_length_dict(reply_graph, reply_nodes, row_node_id)
    root_path_dict = compute_all_root_path_length_dict(reply_graph, reply_nodes, root_node)
    return conversation_depth, path_dict, reply_nodes, result_of_results, root_path_dict, row_node_author_id, row_node_id


def compute_all_path_length_dict(reply_graph, reply_nodes, row_node_id):
    """

    :param reply_graph:
    :param reply_nodes:
    :param row_node_id:
    :return: a dict of (node_id, path_length) -> path
    """
    paths = [(x, nx.all_simple_paths(reply_graph, x, row_node_id)) for x, y in reply_nodes]
    path_dict = {}
    for x, path in paths:
        for single_path in path:
            path_dict[(x, len(single_path) - 1)] = single_path
    return path_dict


def compute_all_root_path_length_dict(reply_graph, reply_nodes, root_node):
    """
    :param root_node:
    :param reply_nodes:
    :param reply_graph:
    :return: a dict of (node_id, path_length) -> path
    """
    paths = [(x, nx.all_simple_paths(reply_graph, root_node, x)) for x, y in reply_nodes]
    path_dict = {}
    for x, path in paths:
        for single_path in path:
            path_dict[(x, len(single_path) - 1)] = single_path
    return path_dict


def compute_follower_features(conversation_graph, current_node_id, follower_Graph, result, row_node_author_id,
                              conversation_id):
    """
    This not only computes the follower feature but also adds the beam_node_author to the mix
    :param conversation_graph:
    :param current_node_id:
    :param follower_Graph:
    :param result:
    :param row_node_author_id:
    :param conversation_id:
    :return:
    """
    in_edges = conversation_graph.in_edges(current_node_id, data=True)
    current_node_author_id = None
    result["has_followed_path"] = 0
    result["has_follow_path"] = 0
    try:
        for source, target, attr in in_edges:
            if attr["label"] == "author_of":
                current_node_author_id = source
                result["beam_node_author"] = current_node_author_id
        if nx.has_path(follower_Graph, row_node_author_id, current_node_author_id):
            result["has_follow_path"] = 1
        if nx.has_path(follower_Graph, current_node_author_id, row_node_author_id):
            result["has_followed_path"] = 1
    except networkx.exception.NodeNotFound:
        # logger.debug(
        #    "not all nodes have been downloaded in the follower_network for conversation {}".format(conversation_id))
        pass


def compute_timedelta_feature(current_node_timestamp, result, tweet):
    result["timedelta"] = (tweet.created_at - current_node_timestamp).total_seconds()


def compute_y(conversation_graph, current_node_id, result, tweet):
    """
    a tweet counts as seen (for sure) if it has been replied to by the same author
    :param conversation_graph:
    :param current_node_id:
    :param result:
    :param tweet:
    :return:
    """
    row_twitter_id = tweet.twitter_id
    assert row_twitter_id != current_node_id
    row_author_id = tweet.author_id
    out_edges = conversation_graph.out_edges(current_node_id, data=True)
    result["y"] = 0
    for source, target, out_attr in out_edges:
        # out edges can only be replies
        assert out_attr["label"] == "parent_of"
        in_edges = conversation_graph.in_edges(target, data=True)
        # since target already has a source, there can only be in-edges of type author_of
        for author_id, _, in_attr in in_edges:
            if in_attr["label"] == "author_of":
                if author_id == row_author_id:
                    result["y"] = 1


def compute_reply_features(path_dict, current_node_id, result, row_node_id, conversation_depth):
    """
    this computes the distance of the two tweets based on how many replies stand between them in the tree
    :param path_dict:
    :param current_node_id:
    :param result:
    :return:
    """
    assert current_node_id != row_node_id
    for i in range(2, conversation_depth - 1):
        path_exists = (current_node_id, i) in path_dict
        result_value = 0
        if path_exists:
            result_value = 1
        result["reply_distance_" + str(i)] = result_value


def compute_root_distance_feature(path_dict, current_node_id, result, root_node, row_node_id, conversation_depth):
    result["root_distance_0"] = 0
    if root_node == current_node_id:
        result["root_distance_0"] = 1

    for i in range(1, conversation_depth - 1):
        path_exists = (current_node_id, i) in path_dict
        result_value = 0
        if path_exists:
            result_value = 1
        result["root_distance_" + str(i)] = result_value
