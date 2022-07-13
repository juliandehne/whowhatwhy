from delab.models import Tweet
import networkx as nx


def run():
    replies = Tweet.objects.value_list("id", "twitter_id", "tn_parent_id")

    G = nx.DiGraph()
    edges = []
    for row in replies:
        G.add_node(row[1], id=row[0])
        edges.append((row[2], row[1]))

    G.add_edges_from(edges)
