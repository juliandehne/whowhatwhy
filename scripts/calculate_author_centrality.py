import math
from random import random, Random

import networkx as nx
import pandas as pd

from delab.analytics.author_centrality import compute_conversation_author_centrality
from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.conversation_network import get_nx_conversation_graph, get_root
from django_project.settings import performance_conversation_max_size

debug = False


def run():
    out_put_file = "notebooks/data/author_centrality_remote.pkl"

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

        records += compute_conversation_author_centrality(conversation_id, conversation_paths, reply_graph, root_node, tweets)
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



