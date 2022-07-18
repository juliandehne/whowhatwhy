import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.DjangoTripleDAO import DjangoTripleDAO
from delab.network.conversation_network import compute_author_graph, download_followers, get_participants, \
    download_followers_recursively, prevent_multiple_downloads, restrict_conversations_to_reasonable

"""
The basic idea:
- vision of a graph is defined as an author having a high probability of having seen a random tweet when he was writing!
- P(tweet seen | reply) is 1for a tweet the author replied to
- Note: all the following params might need to be trained with a classifierort
- P(tweet seen | replied to) is 0.8 that mentions the author or replies directly to a tweet of the author
- P(tweet seen | reply of reply) is  1/2 * P(tweet seen | reply) 
- P(tweet seen | replied to of replied to) is  1/4 * P(tweet seen | replied_to)
- P(tweet seen | following_author) is 0.9 
- P(tweet seen | following_author that follows author) is 1/5 * P(tweet seen | following_author)   
  Note 2:  P(answer | tweet seen) should integrate alpha where alpha is computed based on the time that has passed in average when answering tweetss
  
  https://towardsdatascience.com/build-a-simple-neural-network-using-pytorch-38c55158028d
  
  Read probability and answer probability can be viewed as dependent. You can only write if you have read + some sort of interest in answering.
  P(W | R and I) = P(R) + p(I)
"""


def calculate_row(tweet, follower_Graph, conversation_graph):
    """

    :param tweet:
    :return: a dictionary of the tweet history containing the column names as keys and the features as values
    """
    result = {}

    return result


def run():
    """
    This assumes that the follower networks have previously been downloaded
    :return:
    """
    conversation_ids = get_all_conversation_ids()
    conversation_ids_not_downloaded = prevent_multiple_downloads(conversation_ids)
    conversation_ids = np.setdiff1d(conversation_ids, conversation_ids_not_downloaded)
    # conversation_ids = restrict_conversations_to_reasonable(conversation_ids)
    count = 0
    for conversation_id in conversation_ids:
        count += 1
        print("processed {}/{} conversations".format(count, len(conversation_ids)))
        tweets = Tweet.objects.filter(conversation_id=conversation_id)

        # get the follower graph from the db
        networkDAO = DjangoTripleDAO()
        follower_Graph = networkDAO.get_discussion_graph(conversation_id)
        # get the reply graph from the db
        conversation_graph = compute_author_graph(conversation_id)
        records = []
        for tweet in tweets:
            row_dict = calculate_row(tweet, follower_Graph, conversation_graph)
            records.append(row_dict)
        break;
