import networkx as nx
from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship

uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "test"))


def add_follower(follower_id, target_id):
    """
    Creates a follow link from the follower to the one being followed
    :param follower_id:
    :param target_id:
    :return:
    """

    def create_follower_rel(tx):
        tx.run("MERGE (a:Person {id: $follower_id}) "
               "MERGE (b:Person {id: $target_id}) "
               "MERGE (a)-[:FOLLOWS]->(b)",
               follower_id=follower_id, target_id=target_id)

    with driver.session() as session:
        session.write_transaction(create_follower_rel)

    session.close()
    driver.close()


def add_follow_rels(followerpairs):
    """
    :param followerpairs: a list of (follower, and target pairs) i.e. [(1,2), (2,4)...]
    :return:
    """

    def create_follower_rel(tx):
        for pair in followerpairs:
            tx.run("MERGE (a:Person {id: $follower_id}) "
                   "MERGE (b:Person {id: $target_id}) "
                   "MERGE (a)-[:FOLLOWS]->(b)",
                   follower_id=pair[0], target_id=pair[1])

    with driver.session() as session:
        session.write_transaction(create_follower_rel)

    session.close()
    driver.close()


def add_discussion(participant_ids, discussion_id):
    """
    Creates a discussion node that all the participants are connected, too
    :param participant_ids:
    :param discussion_id:
    :return:
    """

    def create_participant_rel(tx):
        for participant_id in participant_ids:
            tx.run("MERGE (a:Person {id: $source_id}) "
                   "MERGE (b:Discussion {id: $target_id}) "
                   "MERGE (a)-[:PARTICIPATESIN]->(b)",
                   source_id=participant_id, target_id=discussion_id)

    with driver.session() as session:
        session.write_transaction(create_participant_rel)

    session.close()
    driver.close()


def get_discussion_graph(discussion_id):
    """
    Get all connectected nodes to a discussion (traversing the discussion -> participants -> follow path)
    :param discussion_id:
    :return:
    """

    query = "match (p:Person)-[:PARTICIPATESIN]->(d) " \
            "match (p2:Person)-[:PARTICIPATESIN]->(d:Discussion{id:"+str(discussion_id)+"}) " \
            "MATCH path = (p)-[:FOLLOWS*1..3]-(p2) return p,p2,relationships(path) as f"

    with driver.session() as session:
        result = session.run(query)
        G = graph_from_cypher(result.graph())

    session.close()
    driver.close()

    return G


def graph_from_cypher(data):
    """Constructs a networkx graph from the results of a neo4j cypher query.
    Example of use:
    >>> result = session.run(query)
    >>> G = graph_from_cypher(result.data())

    Nodes have fields 'labels' (frozenset) and 'properties' (dicts). Node IDs correspond to the neo4j graph.
    Edges have fields 'type_' (string) denoting the type of relation, and 'properties' (dict)."""

    G = nx.MultiDiGraph()

    def add_node(node):
        # Adds node id it hasn't already been added
        u = node.id
        if G.has_node(u):
            return
        G.add_node(u, labels=node._labels, properties=dict(node))

    def add_edge(relation):
        # Adds edge if it hasn't already been added.
        # Make sure the nodes at both ends are created
        for node in (relation.start_node, relation.end_node):
            add_node(node)
        # Check if edge already exists
        u = relation.start_node.id
        v = relation.end_node.id
        eid = relation.id
        if G.has_edge(u, v, key=eid):
            return
        # If not, create it
        G.add_edge(u, v, key=eid, type_=relation.type, properties=dict(relation))

    for d in data:
        for entry in d.values():
            # Parse node
            if isinstance(entry, Node):
                add_node(entry)

            # Parse link
            elif isinstance(entry, Relationship):
                add_edge(entry)
            else:
                raise TypeError("Unrecognized object")
    return G


def get_polarization_measure(discussion_id):
    """
    Uses Neo4j-Internal Mechanism to measure how connected / polarized a discussion is (or else computes it in python)
    :param discussion_id:
    :return:
    """
    pass


def get_groups(discussion_id):
    """
    Uses Neo4j-internal meausres to compute the groups (clusters) of participants in a discussion (or else computes it in python)
    :param discussion_id:
    :return:
    """
    pass
