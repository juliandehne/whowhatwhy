import logging

import networkx as nx
from django.db.models import Q

from delab.models import FollowerNetwork, TweetAuthor, Tweet
from delab.delab_enums import NETWORKRELS
from delab.network.NetworkDAO import NetworkDAO

logger = logging.getLogger(__name__)


def get_network_recursively_helper_forward(sources, recursion_levels=3):
    """
    recursively goes throw the triple table and reconstructs the network moving forward
    :param current_network:
    :param recursion_levels:
    :return:
    """

    if recursion_levels == 0:
        return sources
    else:
        n_sources = [rel[0] for rel in sources]
        fn = FollowerNetwork.objects.filter(source_id__in=n_sources).all()
        n_tuples = [(rel.source_id, rel.relationship, rel.target_id) for rel in fn]
        recursion_levels -= 1
        forward_network = get_network_recursively_helper_forward(n_tuples, recursion_levels)
        return sources + forward_network


def get_network_recursively_helper_backwards(targets, recursion_levels=3):
    """
    recursively goes throw the triple table and reconstructs the network moving backward
    :param current_network:
    :param recursion_levels:
    :return:
    """

    if recursion_levels == 0:
        return targets
    else:
        n_targets = [rel[2] for rel in targets]
        fn = FollowerNetwork.objects.filter(target_id__in=n_targets).all()
        n_tuples = [(rel.source_id, rel.relationship, rel.target_id) for rel in fn]
        recursion_levels -= 1
        forward_network = get_network_recursively_helper_backwards(n_tuples, recursion_levels)

        return targets + forward_network


class DjangoTripleDAO(NetworkDAO):
    def add_follower(self, follower_id, target_id):
        """
        Creates a follow link from the follower to the one being followed
        :param follower_id:
        :param target_id:
        :return:
        """
        try:
            source = TweetAuthor.objects.filter(twitter_id=follower_id).get()
            target = TweetAuthor.objects.filter(twitter_id=target_id).get()
            FollowerNetwork.objects.get_or_create(
                source=source,
                target=target,
                relationship=NETWORKRELS.FOLLOWS
            )
        except TweetAuthor.DoesNotExist as ex:
            logger.error(
                "rel {} -> {} could not be persisted, because source or target are not in database".format(follower_id,
                                                                                                           target_id))
            logger.error(ex)

    def add_follow_rels(self, follower_pairs):
        """
        :param follower_pairs: a list of (follower, and target pairs) i.e. [(1,2), (2,4)...]
        :return:
        """
        for pair in follower_pairs:
            self.add_follower(pair[0], pair[1])

    def add_discussion(self, participant_ids, conversation_id):
        """
        Creates a discussion node that all the participants are connected, too
        (not needed in django implementation)
        :param participant_ids:
        :param conversation_id:
        :return:
        """
        pass

    def get_discussion_graph(self, conversation_id, recursion_levels=3):
        """
        Get all connectected nodes to a discussion (traversing the discussion -> participants -> follow path)
        :param conversation_id:
        :param recursion_levels:
        :return:
        """
        author_twitter_ids = list(
            Tweet.objects.filter(conversation_id=conversation_id).values_list("author_id", flat=True).all())
        authors = TweetAuthor.objects.filter(twitter_id__in=author_twitter_ids)
        lvl1_network = FollowerNetwork.objects.filter(Q(source__in=authors) | Q(target__in=authors)).all()
        g = nx.DiGraph()
        if lvl1_network.count() > 0:
            lvl1_tuples = [(rel.source_id, rel.relationship, rel.target_id) for rel in lvl1_network]
            network_tuples = set(get_network_recursively_helper_backwards(lvl1_tuples, recursion_levels))
            network_tuples = set(get_network_recursively_helper_forward(lvl1_tuples, recursion_levels))
            follow_pais = [(triple[0], triple[2]) for triple in network_tuples if triple[1] == NETWORKRELS.FOLLOWS]
            g.add_edges_from(follow_pais, name=NETWORKRELS.FOLLOWS)
        return g

    def get_polarization_measure(self, conversation_id):
        """
        :param conversation_id:
        :return:
        """
        pass
