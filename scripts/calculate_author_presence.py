import networkx as nx
from matplotlib import pyplot as plt

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.conversation_network import get_nx_conversation_graph


def run():
    conversation_ids = get_all_conversation_ids()
    count = 0
    for conversation_id in conversation_ids:
        count += 1
        print("processed {}/{} conversations".format(count, len(conversation_ids)))

        G = get_nx_conversation_graph(conversation_id)

        author_tweet_pairs = Tweet.objects.filter(conversation_id=conversation_id).only("twitter_id", "author_id")

        G2 = nx.MultiDiGraph()

        G2.add_nodes_from(G.nodes())
        G2.add_edges_from(G.edges(), label="reply_to")

        for result_pair in author_tweet_pairs:
            G2.add_node(result_pair.author_id, author=result_pair.author_id)
            G2.add_edge(result_pair.author_id, result_pair.twitter_id, label="author_of")

        if len(G2.edges()) > 10:
            print(G2)
            pos = nx.kamada_kawai_layout(G2)
            nx.draw(G2, pos, with_labels=False)
            nx.draw_networkx_edge_labels(G2, pos)
            plt.show()
            break
