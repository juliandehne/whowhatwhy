import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.DjangoTripleDAO import DjangoTripleDAO
from delab.network.author_presence import calculate_row
from delab.network.conversation_network import compute_author_graph, download_followers, get_participants, \
    download_followers_recursively, prevent_multiple_downloads, restrict_conversations_to_reasonable, get_root, \
    get_tweet_subgraph, paint_reply_graph, get_nx_conversation_graph, compute_author_graph_helper
from delab.network.conversation_network import paint_bipartite_author_graph

debug = True


def run():
    """
    This assumes that the follower networks have previously been downloaded
    :return:
    """
    conversation_ids = get_all_conversation_ids()
    # conversation_ids_not_downloaded = prevent_multiple_downloads(conversation_ids)
    # conversation_ids = np.setdiff1d(conversation_ids, conversation_ids_not_downloaded)
    # conversation_ids = restrict_conversations_to_reasonable(conversation_ids)
    count = 0
    records = []
    for conversation_id in conversation_ids:
        count += 1
        print("processed {}/{} conversations".format(count, len(conversation_ids)))
        tweets = Tweet.objects.filter(conversation_id=conversation_id)

        # for debug
        if (tweets.count() > 20 and debug) or tweets.count() < 5:
            continue

        # get the follower graph from the db
        networkDAO = DjangoTripleDAO()
        follower_Graph = networkDAO.get_discussion_graph(conversation_id)
        # get the reply graph from the db
        reply_graph = get_nx_conversation_graph(conversation_id)
        if debug:
            path = nx.dag_longest_path(reply_graph)
            if len(path) < 4:
                continue

        root_node = get_root(reply_graph)
        conversation_graph = compute_author_graph_helper(reply_graph, conversation_id)

        if debug:
            for node in conversation_graph.nodes(data=True):
                print(node)
            paint_bipartite_author_graph(conversation_graph, root_node)
            paint_reply_graph(reply_graph)

        for tweet in tweets:
            row_dict = calculate_row(tweet, reply_graph, follower_Graph, conversation_graph, root_node)
            # empty dictionaries evaluate to false
            records += row_dict
        # print(records)
        if debug:
            break

    df = pd.DataFrame.from_records(records)
    with pd.option_context('display.max_rows', None, 'display.max_columns',
                           None):  # more options can be specified also
        # print(df[df["y"] == 1])
        # print(df)
        # print(df[["has_followed_path", "has_follow_path"]])
        print(df.describe())
        if not debug:
            df.to_pickle("notebooks/data/vision_graph_data.pkl")
