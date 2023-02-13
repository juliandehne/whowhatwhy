"""
computes a measure how
"""

from delab.api.api_util import get_all_twitter_conversation_ids
from delab.models import Mentions
from delab.network.conversation_network import get_mention_graph, GRAPH
import pickle


def run():
    conversation_ids = get_all_twitter_conversation_ids()
    conversation_ids_from_mentions = set(Mentions.objects.values_list("conversation_id", flat=True))
    conversations_with_mentions = conversation_ids_from_mentions.intersection(conversation_ids)
    assert len(conversations_with_mentions) > 0
    conversation_metrics = {}
    for conversation_id in conversations_with_mentions:
        try:
            mentions_g = get_mention_graph(conversation_id)
            selected_edges = [(u, v) for u, v, e in mentions_g.edges(data=True) if
                              e['label'] == GRAPH.LABELS.MENTIONS]
            # reply_tree_edges = [(u, v) for u, v, e in mentions_g.edges(data=True) if
            #                    e['label'] == GRAPH.LABELS.PARENT_OF]
            # author_of_edges = [(u, v) for u, v, e in mentions_g.edges(data=True) if
            #                    e['label'] == GRAPH.LABELS.AUTHOR_OF]
            author_seen_count = {}  # counts the number an author has seen based on the mentions he has given
            for mentioner, mentionee in selected_edges:
                if mentioner not in author_seen_count:
                    author_seen_count[mentioner] = 0
                author_seen_count[mentioner] += 1
            conversation_metrics[conversation_id] = author_seen_count
            # print(selected_edges)
            print(author_seen_count)
        except AssertionError:
            continue

    out_put_file = "notebooks/data/conversation_mentions.pkl"

    pickle.dump(conversation_metrics, open(out_put_file, "wb"))
