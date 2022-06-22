from neo4j import GraphDatabase

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

    driver.close()



def get_discussion_graph(discussion_id):
    """
    Get all connectected nodes to a discussion (traversing the discussion -> participants -> follow path)
    :param discussion_id:
    :return:
    """
    pass


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
