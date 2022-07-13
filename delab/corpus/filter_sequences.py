import itertools

import networkx as nx

from delab.models import Tweet


def get_all_reply_paths(conversation_id, min_path_length, required_max_path_length):
    replies = Tweet.objects.filter(conversation_id=conversation_id).only("id", "twitter_id", "tn_parent_id")
    G = nx.DiGraph()
    edges = []
    nodes = []
    for row in replies:
        nodes.append(row.twitter_id)
        G.add_node(row.twitter_id, id=row.id)
        if row.tn_parent_id is not None:
            edges.append((row.tn_parent_id, row.twitter_id))
    G.add_edges_from(edges)
    all_paths = []
    nodes_combs = itertools.combinations(G.nodes, 2)
    for source, target in nodes_combs:
        paths = nx.all_simple_paths(G, source=source, target=target, cutoff=required_max_path_length)

        for path in paths:
            if path not in all_paths and path[::-1] not in all_paths and len(path) >= min_path_length:
                all_paths.append(path)
    return all_paths


def get_path(twitter_id, conversation_id, min_path_length=3, required_max_path_length=4):
    paths = get_all_reply_paths(conversation_id, min_path_length, required_max_path_length)
    current_best_path_index = None
    current_best_score = 0
    index_count = 0
    for path in paths:
        if twitter_id in path:
            p_index = path.index(twitter_id)
            previous_tweets = p_index
            following_tweets = len(path) - p_index - 1
            middleness_score = min(previous_tweets, following_tweets) - abs(previous_tweets - following_tweets)
            if middleness_score > current_best_score:
                current_best_path_index = index_count
            current_best_score = max(current_best_score, middleness_score)
        index_count += 1
    if current_best_path_index is None:
        return None
    return paths[current_best_path_index]