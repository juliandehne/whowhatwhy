import networkx as nx

from delab.models import Tweet
from delab.network.DjangoTripleDAO import DjangoTripleDAO


def run():
    conversation_ids = set(Tweet.objects.values_list('conversation_id', flat=True))
    dao = DjangoTripleDAO()
    graphs = [(conversation_id, dao.get_discussion_graph(conversation_id)) for conversation_id in conversation_ids]
    # non_empty_graphs = [x for x in graphs if x]

    data_dir = "notebooks/followernetworks"
    out_fp = f'{data_dir}/graphs'
    for conversation_id, g in graphs:
        nx.write_gpickle(g, f"{out_fp}/{conversation_id}_Gs.gpickle")

    for conversation_id, g in graphs:
        nx.read_gpickle(f"{out_fp}/{conversation_id}_Gs.gpickle")

