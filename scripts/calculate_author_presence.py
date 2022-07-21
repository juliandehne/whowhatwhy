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
    get_tweet_subgraph, paint_reply_graph
from delab.network.conversation_network import paint_bipartite_author_graph


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

        # get the follower graph from the db
        networkDAO = DjangoTripleDAO()
        follower_Graph = networkDAO.get_discussion_graph(conversation_id)
        # get the reply graph from the db
        conversation_graph = compute_author_graph(conversation_id)

        # paint_bipartite_author_graph(conversation_graph)

        subgraph = get_tweet_subgraph(conversation_graph)
        root_node = get_root(subgraph)

        # paint_reply_graph(subgraph)

        for tweet in tweets:
            row_dict = calculate_row(tweet, follower_Graph, conversation_graph, root_node)
            # empty dictionaries evaluate to false
            records += row_dict

        # break

    df = pd.DataFrame.from_records(records)
    with pd.option_context('display.max_rows', None, 'display.max_columns',
                           None):  # more options can be specified also
        # print(df[df["y"] == 1])
        # print(df)
        # print(df[["has_followed_path", "has_follow_path"]])
        print(df.describe())
        df.to_pickle("notebooks/data/vision_graph_data.pkl")

