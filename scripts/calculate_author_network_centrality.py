"""
Calculate the author centrality based on the
"""

from random import Random

import networkx as nx

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.conversation_network import compute_author_interaction_graph, get_root_author, \
    paint_bipartite_author_graph, compute_author_graph
from matplotlib import pyplot as plt

debug = True


def run():
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
        author_graph = compute_author_graph(conversation_id)
        if debug:
            nx.draw(author_graph, with_labels=True, node_size=1000, font_size=8, font_weight="bold", width=0.75,
                    edgecolors='gray')
            plt.show(block=False)

        author_interaction_graph = compute_author_interaction_graph(conversation_id)
        if debug:
            nx.draw(author_interaction_graph, with_labels=True, node_size=1000, font_size=8, font_weight="bold",
                    width=0.75,
                    edgecolors='gray')
            plt.show(block=False)

        if debug:
            break
