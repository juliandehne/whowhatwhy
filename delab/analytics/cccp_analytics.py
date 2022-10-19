import networkx as nx
import pandas as pd

from delab.api.api_util import get_author_tweet_map
from delab.models.corpus_project_models import Tweet
from delab.network.conversation_network import get_nx_conversation_graph, get_root

MEASURES = ["repetition_prob", "baseline_vision", "centrality", "mean"]


def compute_all_cccp_authors():
    df = prepare_metric_records()
    candidate_lists = []
    measure_authors_dictionary = {}
    author2measure = {}
    for measure in MEASURES:
        candidate_list = compute_cccp_candidate_authors(df, measure=measure)
        for conversation_id, author_id in candidate_list:
            if measure in measure_authors_dictionary:
                current_author_list = measure_authors_dictionary[measure]
                current_author_list.append(author_id)
                measure_authors_dictionary[measure] = current_author_list
            else:
                measure_authors_dictionary[measure] = [author_id]
            author2measure[author_id] = measure
        candidate_lists += candidate_list
    return candidate_lists, measure_authors_dictionary, author2measure


def get_central_author_tweet_queryset(conversation_id, tw_author_id):
    tweets = Tweet.objects.filter(conversation_id=conversation_id).all()
    return tweets, tw_author_id


def prepare_metric_records():
    """
    prepares a dataframe with the tweet author data and and the conversation_author_metrics
    @return:
    """
    records = []
    tweets = Tweet.objects.all()
    for tweet in tweets:
        if tweet.tw_author is None:
            continue
        tweet_record = {"tweet_id": tweet.id, "text": tweet.text, "conversation_id": tweet.conversation_id,
                        "author_id": tweet.tw_author.id}
        metrics = tweet.tw_author.conversationauthormetrics_set.filter(
            conversation_id=tweet.conversation_id)
        if not metrics.exists():
            continue
        else:
            author_metrics = metrics.get()
            tweet_record["centrality"] = author_metrics.centrality
            tweet_record["baseline_vision"] = author_metrics.baseline_vision
            tweet_record["n_posts"] = author_metrics.n_posts
            records.append(tweet_record)
    df = pd.DataFrame.from_records(records)
    return df


def compute_cccp_candidate_authors(df, measure="mean"):
    """
    @param df: the dataframe containing the metrics centrality, baseline_vision etc.
    @param measure: the measure to be used for filtering candidates, such as "mean" for all measures, or "centrality"
    @return: a list of pairs (conversation_id, author_id)
    """
    df_central_authors = df.drop(
        ["text"], axis=1)
    df_repetition_probs = df.drop(
        ["text",
         "centrality", "baseline_vision", "n_posts", "author_id"], axis=1)
    # %%
    df_repetition_probs = df_repetition_probs.groupby(["conversation_id"]).count()
    grouped_ca = df_central_authors.groupby(["conversation_id", "author_id"]).mean()
    grouped_ca = grouped_ca.drop("tweet_id", axis=1)
    grouped_ca = grouped_ca.join(df_repetition_probs)
    grouped_ca = grouped_ca.assign(repetition_prob=grouped_ca.n_posts / grouped_ca.tweet_id)
    grouped_ca = grouped_ca.drop("tweet_id", axis=1)
    if measure == "mean":
        grouped_ca = grouped_ca.apply(lambda x: x / x.max())
        grouped_ca['mean'] = grouped_ca.mean(axis=1)
        mean_largest = grouped_ca.nlargest(20, "mean")
    if measure == "repetition_prob" or measure == "baseline_vision" or measure == "centrality":
        mean_largest = grouped_ca.nlargest(20, measure)

    # this is the result list, first element of tuple is conversation, second the author
    result = mean_largest.index.tolist()
    # print(result)
    return result


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
    :param conversation_id:
    :return:
    """
    author2baseline = {}
    reply_graph, removed, changed = get_nx_conversation_graph(conversation_id, merge_subsequent=True)
    root = get_root(reply_graph)
    tweet2author, author2tweets = get_author_tweet_map(conversation_id)
    for node in removed:
        tweet2author.pop(node, None)
    for author in author2tweets.keys():
        n_posts = len(author2tweets[author])
        root_distance_measure = 0
        reply_vision_measure = 0
        for tweet in author2tweets[author]:
            if tweet in removed:
                continue
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
