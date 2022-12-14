"""
Calculate the author centrality based on the
"""

from random import Random

import networkx as nx

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet, ConversationAuthorMetrics
from delab.network.conversation_network import compute_author_interaction_graph, get_root_author, \
    paint_bipartite_author_graph, compute_author_graph
from matplotlib import pyplot as plt

debug = False


def run():
    randomizer = Random()
    conversation_ids = get_all_conversation_ids()
    calculated_ids = set(ConversationAuthorMetrics.objects.filter(katz_centrality__isnull=False).values_list("conversation_id", flat=True))
    conversation_ids = list(set(conversation_ids) - calculated_ids)
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

        katz_centrality = nx.katz_centrality(author_interaction_graph)
        try:
            betweenness_centrality = nx.betweenness_centrality(author_interaction_graph)
        except ValueError:
            betweenness_centrality = {}

        author_ids = set(
            Tweet.objects.filter(conversation_id=conversation_id).values_list("author_id", flat=True).all())
        for author_id in author_ids:
            closeness_centrality = nx.closeness_centrality(author_interaction_graph, author_id)
            if ConversationAuthorMetrics.objects.filter(conversation_id=conversation_id).filter(
                    author__twitter_id=author_id).exists():
                metric = ConversationAuthorMetrics.objects.filter(conversation_id=conversation_id).filter(
                    author__twitter_id=author_id).get()
                metric.closeness_centrality = closeness_centrality
                metric.betweenness_centrality = betweenness_centrality.get(author_id, None)
                metric.katz_centrality = katz_centrality.get(author_id, None)
                metric.save(update_fields=["closeness_centrality", "betweenness_centrality", "katz_centrality"])

        if debug:
            break
