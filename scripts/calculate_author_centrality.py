import math
from random import random, Random

import networkx as nx
import pandas as pd

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.conversation_network import get_nx_conversation_graph, get_root
from django_project.settings import performance_conversation_max_size

debug = False


def run():
    out_put_file = "notebooks/data/author_centrality_local.pkl"

    randomizer = Random()
    conversation_ids = get_all_conversation_ids()
    randomizer.shuffle(conversation_ids)
    count = 0
    records = []
    for conversation_id in conversation_ids:
        print("processed {}/{} conversations".format(count, len(conversation_ids)))
        tweets = Tweet.objects.filter(conversation_id=conversation_id)

        # for debug
        # or tweets.count() > performance_conversation_max_size
        if (tweets.count() > 20 and debug) or tweets.count() < 5:
            continue

        count += 1
        # get the reply graph from the db
        reply_graph = get_nx_conversation_graph(conversation_id)
        longest_path = nx.dag_longest_path(reply_graph)
        if len(longest_path) < 4:
            continue

        root_node = get_root(reply_graph)

        conversation_paths = []
        for node in reply_graph:
            if reply_graph.out_degree(node) == 0:  # it's a leaf
                conversation_paths.append(nx.shortest_path(reply_graph, root_node, node))

        tweet2author_dict = {}
        tweet2platform_dict = {}
        for tweet in tweets:
            tweet2platform_dict[tweet.twitter_id] = tweet.platform
            tweet2author_dict[tweet.twitter_id] = tweet.author_id

        # print(len(conversation_paths))

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
        if debug:
            break

    df = pd.DataFrame.from_records(records)
    df.fillna(0, inplace=True)
    with pd.option_context('display.max_rows', None, 'display.max_columns',
                           None):  # more options can be specified also
        # print(df[df["y"] == 1])
        # print(df)
        # print(df[["has_followed_path", "has_follow_path"]])

        print(df.describe())
        if not debug:
            df.to_pickle(out_put_file)


def compute_centrality_bias(path, node):
    i = path.index(node) + 1
    centrality = math.ceil(len(path) / 2)
    node_centrality = abs(centrality - i) / (len(path) - 1)
    node_centrality_to_1 = 1 - node_centrality
    return node_centrality_to_1
