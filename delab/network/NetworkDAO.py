class NetworkDAO:
    def add_follower(self, follower_id, target_id):
        """
        Creates a follow link from the follower to the one being followed
        :param follower_id:
        :param target_id:
        :return:
        """
        pass

    def add_follow_rels(self, followerpairs):
        """
        :param followerpairs: a list of (follower, and target pairs) i.e. [(1,2), (2,4)...]
        :return:
        """
        pass

    def add_discussion(self, participant_ids, conversation_id):
        """
        Creates a discussion node that all the participants are connected, too
        :param participant_ids:
        :param conversation_id:
        :return:
        """
        pass

    def get_discussion_graph(self, conversation_id):
        """
        Get all connectected nodes to a discussion (traversing the discussion -> participants -> follow path)
        :param conversation_id:
        :return:
        """
        pass

    def get_polarization_measure(self, conversation_id):
        """
        Uses Neo4j-Internal Mechanism to measure how connected / polarized a discussion is (or else computes it in python)
        :param conversation_id:
        :return:
        """
        pass