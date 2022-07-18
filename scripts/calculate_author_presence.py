import networkx as nx
from matplotlib import pyplot as plt

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.conversation_network import compute_author_graph

"""
The basic idea:
- vision of a graph is defined as an author having a high probability of having seen a random tweet when he was writing!
- P(tweet seen | reply) is 1for a tweet the author replied to
- Note: all the following params might need to be trained with a classifier
- P(tweet seen | replied to) is 0.8 that mentions the author or replies directly to a tweet of the author
- P(tweet seen | reply of reply) is  1/2 * P(tweet seen | reply) 
- P(tweet seen | replied to of replied to) is  1/4 * P(tweet seen | replied_to)
- P(tweet seen | following_author) is 0.9 
- P(tweet seen | following_author that follows author) is 1/5 * P(tweet seen | following_author)   
  Note 2:  P(answer | tweet seen) should integrate alpha where alpha is computed based on the time that has passed in average when answering tweetss
  
  Read probability and answer probability can be viewed as dependent. You can only write if you have read + some sort of interest in answering.
  P(W | R and I) = P(R) + p(I)
"""


def run():
    conversation_ids = get_all_conversation_ids()
    count = 0
    for conversation_id in conversation_ids:
        count += 1
        print("processed {}/{} conversations".format(count, len(conversation_ids)))
        if 30 > Tweet.objects.filter(conversation_id=conversation_id).count() > 10:
            draw_author_conversation_dist(conversation_id)
            break;


def draw_author_conversation_dist(conversation_id):
    G2 = compute_author_graph(conversation_id)
    # Specify the edges you want here
    red_edges = [(source, target, attr) for source, target, attr in G2.edges(data=True) if
                 attr['label'] == 'author_of']
    # edge_colours = ['black' if edge not in red_edges else 'red'
    #                for edge in G2.edges()]
    black_edges = [edge for edge in G2.edges(data=True) if edge not in red_edges]
    # Need to create a layout when doing
    # separate calls to draw nodes and edges
    pos = nx.multipartite_layout(G2)
    nx.draw_networkx_nodes(G2, pos, node_size=400)
    nx.draw_networkx_labels(G2, pos)
    nx.draw_networkx_edges(G2, pos, edgelist=red_edges, edge_color='red', arrows=True)
    nx.draw_networkx_edges(G2, pos, edgelist=black_edges, arrows=True)
    plt.show()
