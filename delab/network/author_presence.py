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
import networkx as nx

from delab.models import Tweet
from delab.network.conversation_network import get_root


def calculate_row(tweet: Tweet, follower_Graph: nx.MultiDiGraph, conversation_graph: nx.MultiDiGraph, rootnode: int):
    """

    :param conversation_graph: directed graph that represents the conversation tree, node ids are twitter ids
    :param follower_Graph: directed graph that represents the follower structures, node ids are the author ids
    :param tweet:
    :return: a dictionary of the tweet history containing the column names as keys and the features as values
    """
    result_of_results = []
    row_node_id = tweet.twitter_id
    reply_nodes = [(x, y) for x, y in conversation_graph.nodes(data=True) if y['subset'] == "tweets"]
    for current_node_id, current_node_attr in reply_nodes:
        result = {}
        current_node_timestamp = current_node_attr["created_at"]
        if tweet.created_at > current_node_timestamp:
            # we are only looking at the picture before the current tweet
            if row_node_id != current_node_id:
                compute_reply_features(conversation_graph, current_node_id, result, row_node_id)
                compute_timedelta_feature(current_node_timestamp, result, tweet)
                compute_root_distance_feature(conversation_graph, current_node_id, result, rootnode)
                compute_y(conversation_graph, current_node_id, result, tweet)
                result["current"] = tweet.twitter_id
                result["beam_node"] = current_node_id
        if result:
            result_of_results.append(result)
    return result_of_results


def compute_root_distance_feature(conversation_graph, current_node_id, result, root_node):
    if root_node != current_node_id:
        result["root_distance_0"] = 0
        for i in range(1, 3):
            paths = list(
                nx.all_simple_paths(conversation_graph, source=root_node, target=current_node_id, cutoff=i))
            assert len(paths) < 2  # it should be a tree so only one path should be returned
            result["root_distance_" + str(i)] = 0
            if "root_distance_" + str(i - 1) in result:
                if not result.get("root_distance_" + str(i - 1)) == 1:
                    result["root_distance_" + str(i)] = len(paths)
            else:
                result["root_distance_" + str(i)] = len(paths)
    else:
        result["root_distance_0"] = 1
        result["root_distance_1"] = 0
        result["root_distance_2"] = 0


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


def compute_reply_features(conversation_graph, current_node_id, result, row_node_id):
    """
    this computes the distance of the two tweets based on how many replies stand between them in the tree
    :param conversation_graph:
    :param current_node_id:
    :param result:
    :param row_node_id:
    :return:
    """

    for i in range(2, 4):
        paths = list(nx.all_simple_paths(conversation_graph, source=current_node_id, target=row_node_id, cutoff=i))
        assert len(paths) < 2  # it should be a tree so only one path should be returned
        result["reply_distance_" + str(i)] = 0
        if "reply_distance_" + str(i - 1) in result:
            if not result.get("reply_distance_" + str(i - 1)) == 1:
                result["reply_distance_" + str(i)] = len(paths)
        else:
            result["reply_distance_" + str(i)] = len(paths)
