import networkx as nx
from matplotlib import pyplot as plt

from delab.network import Neo4jDAO as dao


def run():
    G = dao.get_discussion_graph(1468834105718677504)
    nx.draw(G)
    plt.savefig("somegraph.png")
