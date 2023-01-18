"""
computes a measure how
"""

from delab.api.api_util import get_all_twitter_conversation_ids
from delab.models import Mentions
from delab.network.conversation_network import get_mention_graph, GRAPH


def run():
    conversation_ids = get_all_twitter_conversation_ids()
    conversation_ids_from_mentions = set(Mentions.objects.values_list("conversation_id", flat=True))
    conversations_with_mentions = conversation_ids_from_mentions.intersection(conversation_ids)
    assert len(conversations_with_mentions) > 0
    for conversation_id in conversations_with_mentions:
        try:
            mentions_g = get_mention_graph(conversation_id)
            selected_edges = [(u, v) for u, v, e in mentions_g.edges(data=True) if e['label'] == GRAPH.LABELS.MENTIONS]
            reply_tree_edges = [(u, v) for u, v, e in mentions_g.edges(data=True) if
                                e['label'] == GRAPH.LABELS.PARENT_OF]
            author_of_edges = [(u, v) for u, v, e in mentions_g.edges(data=True) if
                               e['label'] == GRAPH.LABELS.AUTHOR_OF]
            print(selected_edges)
            # print(mentions_g)
        except AssertionError:
            continue
