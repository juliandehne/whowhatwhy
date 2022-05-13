import networkx as nx


def run():


    G = nx.MultiGraph()
    G.add_node('A', role='manager')
    G.add_edge('A', 'B', relation='friend')
    G.add_edge('A', 'C', relation='business partner')
    G.add_edge('A', 'B', relation='classmate')
    # G.nodes['A']['role'] = 'team member'
    G.nodes['B']['role'] = 'engineer'
    print(G.nodes['A']['role'])