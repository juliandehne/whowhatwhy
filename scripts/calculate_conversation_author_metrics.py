import math

import django.db.utils
import networkx as nx
import yaml
from yaml import SafeLoader

from delab.analytics.author_centrality import author_centrality
from delab.api.api_util import get_all_conversation_ids, get_author_tweet_map
from delab.delab_enums import LANGUAGE
from delab.models.corpus_project_models import ConversationAuthorMetrics, Tweet, TweetAuthor
from delab.network.conversation_network import get_nx_conversation_graph, get_root

"""
Computer Metrics about the conversation aggregated on the author level
"""


def run():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        try:
            author2Centrality = {}
            records = author_centrality(conversation_id)
        except AssertionError as ae:
            print("dysfunctional conversation tree found")
            continue
        baseline_visions = calculate_author_baseline_visions(conversation_id)
        for record in records:
            author = record["author"]
            conversation_id = record["conversation_id"]
            centrality_score = record["centrality_score"]
            if author in author2Centrality:
                author2Centrality[author] = author2Centrality[author] + centrality_score
            else:
                author2Centrality[author] = centrality_score

        for author in author2Centrality.keys():
            n_posts = calculate_n_posts(author,
                                        conversation_id)
            centrality_score = author2Centrality[author] / n_posts
            is_root_author_v = is_root_author(author,
                                              conversation_id)
            baseline_vision = baseline_visions[author]

            try:
                tw_author = TweetAuthor.objects.filter(twitter_id=author).get()
                ConversationAuthorMetrics.objects.create(
                    author=tw_author,
                    conversation_id=conversation_id,
                    centrality=centrality_score,
                    n_posts=n_posts,
                    is_root_author=is_root_author_v,
                    baseline_vision=baseline_vision
                )
            except django.db.utils.IntegrityError as saving_metric_exception:
                # print(saving_metric_exception)
                pass
            except django.db.utils.DataError as date_error:
                print(date_error)


def calculate_n_posts(author_id, conversation_id):
    """
    calculate the number of posts an author has written in a conversation
    :return:
    """
    return Tweet.objects.filter(author_id=author_id, conversation_id=conversation_id).count()


def is_root_author(author_id, conversation_id):
    """
    calculate if the author is the originator of the conversation
    :param author_id:
    :param conversation_id:
    :return:
    """
    root_count = Tweet.objects.filter(author_id=author_id, conversation_id=conversation_id,
                                      tn_parent__isnull=True).count()
    return root_count != 0


def calculate_author_baseline_visions(conversation_id):
    """
    calculate the baseline vision of the author for the given conversation
    :param author_id:
    :param conversation_id:
    :return:
    """
    author2baseline = {}
    reply_graph = get_nx_conversation_graph(conversation_id)
    root = get_root(reply_graph)
    tweet2author, author2tweets = get_author_tweet_map(conversation_id)
    for author in author2tweets.keys():
        n_posts = len(author2tweets[author])
        root_distance_measure = 0
        reply_vision_measure = 0
        for tweet in author2tweets[author]:
            if tweet == root:
                root_distance_measure += 1
            else:
                path = next(nx.all_simple_paths(reply_graph, root, tweet))
                root_distance = len(path)
                root_distance_measure += 0.25 ** root_distance
                reply_vision_path_measure = 0

                reply_paths = next(nx.all_simple_paths(reply_graph, root, tweet))
                for previous_tweet in reply_paths:
                    if previous_tweet != tweet:
                        path_to_previous = nx.all_simple_paths(reply_graph, previous_tweet, tweet)
                        path_to_previous = next(path_to_previous)
                        path_length = len(path_to_previous)
                        reply_vision_path_measure += 0.5 ** path_length
                reply_vision_path_measure = reply_vision_path_measure / len(reply_paths)
                reply_vision_measure += reply_vision_path_measure
        root_distance_measure = root_distance_measure / n_posts
        reply_vision_measure = reply_vision_measure / n_posts
        author2baseline[author] = (root_distance_measure + reply_vision_measure) / 2  # un-normalized
        baseline = author2baseline[author]
        assert 0 <= baseline <= 1
    return author2baseline

