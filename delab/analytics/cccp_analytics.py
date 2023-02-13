import django.db.utils
import networkx as nx
import pandas as pd

from delab.analytics.author_centrality import author_centrality
from delab.api.api_util import get_all_conversation_ids
from delab.api.api_util import get_author_tweet_map
from delab.corpus.filter_conversation_trees import get_well_structured_conversation_ids
from delab.models.corpus_project_models import ConversationAuthorMetrics, TweetAuthor
from delab.models.corpus_project_models import Tweet
from delab.network.conversation_network import get_nx_conversation_graph, get_root
from django_project.settings import MAX_CCCP_CONVERSATION_CANDIDATES, CCCP_N_LARGEST

MEASURES = ["repetition_prob", "baseline_vision", "centrality", "mean"]

"""
In this file measures to compute central, comprehensive and consistent author participation (cccp)
are bundled.
"""


def calculate_conversation_author_metrics():
    """
    This computes the available measures like centrality or number of posts aggregated on the level of
    single authors and conversations
    """
    conversation_ids = set(get_all_conversation_ids())
    to_compute_conversation_ids_flows = conversation_ids - set(
       ConversationAuthorMetrics.objects.values_list("conversation_id", flat=True))
    count = 0
    for conversation_id in to_compute_conversation_ids_flows:
        calculate_author_metrics(conversation_id)
        count += 1
        print("computed {}/{} conversation author metrics".format(count, len(conversation_ids)))


def calculate_author_metrics(conversation_id):
    try:
        author2Centrality = {}
        records = author_centrality(conversation_id)

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
            if ConversationAuthorMetrics.objects.filter(conversation_id=conversation_id,
                                                        author__twitter_id=author).exists():
                continue
            n_posts = calculate_n_posts(author,
                                        conversation_id)
            centrality_score = author2Centrality[author] / n_posts
            is_root_author_v = is_root_author(author,
                                              conversation_id)
            baseline_vision = baseline_visions[author]

            if TweetAuthor.objects.filter(twitter_id=author).exists():
                tw_author = TweetAuthor.objects.filter(twitter_id=author).get()
                ConversationAuthorMetrics.objects.create(
                    author=tw_author,
                    conversation_id=conversation_id,
                    centrality=centrality_score,
                    n_posts=n_posts,
                    is_root_author=is_root_author_v,
                    baseline_vision=baseline_vision
                )
    except AssertionError as ae:
        print("dysfunctional conversation tree found, {}".format(ae))
    except django.db.utils.IntegrityError as saving_metric_exception:
        # print(saving_metric_exception)
        pass
    except django.db.utils.DataError as date_error:
        print(date_error)


def compute_all_cccp_authors():
    """
    computes a list of the best authors with the highest cccp scores in order to evaluate the scores
    in a qualitative study
    @return:
    """
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
    conversation_ids = get_well_structured_conversation_ids()
    records = get_author_metrics_using_raw(conversation_ids)
    # select_data_using_django_orm(conversation_ids, records)
    df = pd.DataFrame.from_records(records)
    return df


def get_author_metrics_using_raw(conversation_ids):
    """
    this function is needed because using the django relational mapper, the query is way to slow
    this is due to conversation_id not being a foreign key in all the related tables (todo)
    @param conversation_ids:
    @return:
    """
    records = []
    metrics = ConversationAuthorMetrics.objects.filter(conversation_id__in=conversation_ids).raw(
        "SELECT cam.id, dt.id as tweet_id, cam.conversation_id, cam.author_id, text, dt.twitter_id, "
        "is_toxic, toxic_value, n_posts, "
        "centrality, baseline_vision, n_posts, is_root_author "
        "FROM delab_tweet dt join delab_conversationauthormetrics cam "
        "on dt.conversation_id = cam.conversation_id and dt.tw_author_id = cam.author_id")
    for tweet in metrics:
        tweet_record = {"tweet_id": tweet.tweet_id, "text": tweet.text, "conversation_id": tweet.conversation_id,
                        "author_id": tweet.author_id, "centrality": tweet.centrality,
                        "baseline_vision": tweet.baseline_vision, "n_posts": tweet.n_posts}
        records.append(tweet_record)
    return records


def select_data_using_django_orm(conversation_ids, records):
    """
    @deprecated
    loads the data using djano object relational mapper. Takes too long for the big dataset
    @param conversation_ids:
    @param records:
    @return:
    """
    tweets = Tweet.objects.filter(tn_parent__isnull=False, conversation_id__in=conversation_ids).all()
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


def compute_cccp_candidate_authors(df, measure="mean"):
    """
    @param df: the dataframe containing the metrics centrality, baseline_vision etc.
    @param measure: the measure to be used for filtering candidates, such as "mean" for all measures, or "centrality"
    @return: a list of pairs (conversation_id, author_id)
    """

    df_central_authors = df.drop(
        ["text"], axis=1)
    root_author_ids = set(Tweet.objects.filter(tn_parent__isnull=True).values_list("tw_author__id", flat=True))
    df_central_authors = df_central_authors[~df_central_authors["author_id"].isin(root_author_ids)]
    n_posts = df_central_authors["n_posts"]
    df_central_authors["centrality"] = df_central_authors["centrality"] * n_posts
    df_central_authors["baseline_vision"] = df_central_authors["baseline_vision"] * n_posts
    df_central_authors["n_posts"] = df_central_authors["n_posts"] * n_posts
    df_repetition_probs = df.drop(
        ["text",
         "centrality", "baseline_vision", "n_posts", "author_id"], axis=1)

    df_repetition_probs = df_repetition_probs.groupby(["conversation_id"]).count()
    grouped_ca = df_central_authors.groupby(["conversation_id", "author_id"]).mean()
    grouped_ca = grouped_ca.drop("tweet_id", axis=1)
    grouped_ca = grouped_ca.join(df_repetition_probs)
    grouped_ca = grouped_ca.assign(repetition_prob=grouped_ca.n_posts / grouped_ca.tweet_id)
    grouped_ca = grouped_ca.drop("tweet_id", axis=1)
    if measure == "mean":
        grouped_ca = grouped_ca.apply(lambda x: x / x.max())
        grouped_ca['mean'] = grouped_ca.mean(axis=1)
        mean_largest = grouped_ca.nlargest(CCCP_N_LARGEST, "mean")
    if measure == "repetition_prob" or measure == "baseline_vision" or measure == "centrality":
        mean_largest = grouped_ca.nlargest(CCCP_N_LARGEST, measure)

    # this is the result list, first element of tuple is conversation, second the author
    result = mean_largest.index.tolist()

    # result = ((conversation_id, author_id) for (conversation_id, author_id) in result if
    #          author_id not in root_author_ids)
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
