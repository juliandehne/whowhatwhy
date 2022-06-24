import networkx as nx
from matplotlib import pyplot as plt

from delab.models import Tweet
from delab.network.DjangoTripleDAO import DjangoTripleDAO


def run():
    # conversation_ids = set(Tweet.objects.values_list('conversation_id', flat=True))
    conversation_ids = [1468859842706259972]  # debug why this is not working
    dao = DjangoTripleDAO()
    graphs = [(conversation_id, dao.get_discussion_graph(conversation_id)) for conversation_id in conversation_ids]
    # non_empty_graphs = [x for x in graphs if x]

    data_dir = "notebooks/followernetworks"
    out_fp = f'{data_dir}/graphs'
    picture_out_fp = f'{data_dir}/graphpictures'
    for conversation_id, g in graphs:
        if not nx.is_empty(g):
            nx.write_gpickle(g, f"{out_fp}/{conversation_id}_Gs.gpickle")
            gn = nx.read_gpickle(f"{out_fp}/{conversation_id}_Gs.gpickle")
            nx.draw(gn, with_labels=True)
            plt.savefig(f"{picture_out_fp}/'{conversation_id}.png", dpi=300, bbox_inches='tight')
            # plt.show()
        else:
            print("no graphs found for convesation {}".format(conversation_id))
