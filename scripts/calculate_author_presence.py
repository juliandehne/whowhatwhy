import random

import networkx as nx
import pandas as pd

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.DjangoTripleDAO import DjangoTripleDAO
from delab.analytics.author_presence import calculate_row
from delab.network.conversation_network import get_root, \
    paint_reply_graph, get_nx_conversation_graph, compute_author_graph_helper
from delab.network.conversation_network import paint_bipartite_author_graph
from django_project.settings import performance_conversation_max_size


def run():
    """
    This assumes that the follower networks have previously been downloaded
    :return:
    """
    debug = False

    # row_function = calculate_forward_row
    row_function = calculate_row # this would do the author has replied predictions
    # row_function = calculate_baseline_row

    # out_put_file = "notebooks/data/vision_graph_data.pkl"
    out_put_file = "notebooks/data/vision_graph_data_remote_23_08_22.pkl"
    # out_put_file = "notebooks/data/vision_graph_data_local_22_08_22.pkl"
    # out_put_file = "notebooks/data/vision_forward_graph_data_08_09_22.pkl"
    # out_put_file = "notebooks/data/vision_baseline_graph_data.pkl"
    conversation_ids = get_all_conversation_ids()
    calculate_conversation_dataframe(conversation_ids, debug, out_put_file, row_function)


def calculate_conversation_dataframe(conversation_ids, debug, out_put_file, row_function):
    # conversation_ids_not_downloaded = prevent_multiple_downloads(conversation_ids)
    # conversation_ids = np.setdiff1d(conversation_ids, conversation_ids_not_downloaded)
    # conversation_ids = restrict_conversations_to_reasonable(conversation_ids)
    random.shuffle(conversation_ids)
    count = 0
    records = []
    for conversation_id in conversation_ids:
        print("processed {}/{} conversations".format(count, len(conversation_ids)))
        tweets = Tweet.objects.filter(conversation_id=conversation_id).all()

        # for debug
        if (tweets.count() > 20 and debug) or tweets.count() < 5 or tweets.count() > performance_conversation_max_size:
            continue

        count += 1
        # debugging different sizes records
        # if count > 30:
        #     break

        # get the follower graph from the
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
            row_dict = row_function(tweet, reply_graph, follower_Graph, conversation_graph, root_node)
            # empty dictionaries evaluate to false
            records += row_dict
        # print(records)
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
