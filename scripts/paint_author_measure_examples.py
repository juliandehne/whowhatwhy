import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.pyplot import text
from networkx.drawing.nx_pydot import graphviz_layout

from delab.network.conversation_network import paint_reply_graph, get_root, add_attributes_to_plot


def run():
    edges = [(1, 2), (1, 3), (3, 4), (3, 5), (5, 7), (5, 6), (6, 8), (7, 9)]
    authors = {
        1: "A", 2: "B", 3: "C", 4: "D", 5: "A", 7: "D", 6: "B", 8: "E", 9: "E"
    }
    labels = {}
    for node, author in authors.items():
        labels[node] = "(" + str(node) + ", " + author + ")"
    g = nx.DiGraph()
    for node, author in authors.items():
        g.add_node(node, author=author)

    g.add_edges_from(edges)

    assert nx.is_tree(g)
    root = get_root(g)
    tree = nx.bfs_tree(g, root)

    colors = ["pink", "red", "violet", "blue",
              "turquoise", "limegreen", "gold", "brown"]  # use hex colors here, if desired.
    author_names = set(authors.values())
    author2color = {}
    i = 0
    for author_name in author_names:
        author2color[author_name] = colors[i]
        i += 1
    color_dict = []
    for node in tree.nodes():
        author = authors[node]
        color_dict.append(author2color[author])

    # d = dict(tree.degree)
    pos = graphviz_layout(tree, prog="dot")
    nx.draw_networkx_labels(tree, labels=labels, pos=pos)
    # nx.draw_networkx_labels(tree, pos)
    nx.draw(tree, pos, labels=labels, node_color=color_dict, node_size=2000)
    # for node, (x, y) in pos.items():
    #     text(x, y, node, fontsize=d[node] * 5, ha='center', va='center')
    # nx.draw_networkx_nodes(tree, pos=pos)
    plt.show(block=False)
    plt.savefig("/home/dehne/ownCloud/julian/paper/author_vision_draft_example.png", format="PNG")
