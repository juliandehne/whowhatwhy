import csv
from functools import partial

from delab.corpus.download_conversations import download_conversations
from delab.delab_enums import LANGUAGE
from delab.models import Tweet, ModerationCandidate2, TwTopic, SimpleRequest
import ast

MODTOPIC2 = "moderationdictmining"


def download_mod_tweets(recent=True):
    for lang in LANGUAGE:
        with open("delab/mm/FunctionPhrases.csv") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            next(reader, None)  # skip the headers
            download_mod_tweets_for_language(reader, lang, recent)


def tweet_filter(query: str, tweet: Tweet):
    """
    this asserts that the tweet will be automatically linked to the candidate and the simple request containing the query for later analysis
    :param query:
    :param tweet:
    :return:
    """

    # create the topic and save it to the db
    topic, created = TwTopic.objects.get_or_create(
        title=MODTOPIC2
    )
    simple_request, created2 = SimpleRequest.objects.get_or_create(
        title=query,
        topic=topic
    )
    tweet.simple_request = simple_request
    # tweet.topic = topic
    if Tweet.objects.filter(twitter_id=tweet.twitter_id).exists():
        tweet = Tweet.objects.filter(twitter_id=tweet.twitter_id).first()
    else:
        tweet.save()

    try:
        contained = test_tweet_matches_dict(query, tweet)
        if contained:
            ModerationCandidate2.objects.get_or_create(
                tweet=tweet
            )

    except Exception as ex:
        print(ex)
    return tweet


def test_tweet_matches_dict(query, tweet):
    """
    because the whole conversation is always being downloaded the references to which was the original candidate
    was lost. For this reason the text is checked for containment of the keywords of the query.
    The is a low probability this will produce additional candidates.
    :param query:
    :param tweet:
    :return:
    """
    contained = True
    index_original_query_end = query.index("is:reply")
    query = query[:index_original_query_end]
    keywords = query.replace("(", "").replace(")", "").replace("-", "").replace("\"", "")
    for item in keywords.split(" "):
        if item in tweet.text:
            contained = contained and True
        else:
            contained = False
    return contained


def download_mod_tweets_for_language(reader, lang, recent):
    """
    This function extracts the phrases from the csv sheet
    :param reader:
    :param lang:
    :param recent:
    :return:
    """
    for row in reader:
        if lang == LANGUAGE.ENGLISH:
            queries = row[8]
            download_mod_helper(lang, queries, recent)
        else:
            if lang == LANGUAGE.GERMAN:
                queries = row[9]
                download_mod_helper(lang, queries, recent)


def generate_contexts():
    # interesting poltical contexts from  https://raw.githubusercontent.com/twitterdev/twitter-context-annotations/main/files/evergreen-context-entities-20220601.csv
    start = "(context:131.900740740468191232 OR "
    # political issues, political talk, politics europe, political news
    contexts = ["131.840159122012102656", "131.1488973753274929152", "131.847878884917886977",
                "131.1281313284952485889", "22.1281313284952485889", "3.10027336130"]
    for elem in contexts[:-1]:
        start = start + "context:{} OR ".format(elem)
    start = start + "context:{})".format(contexts[-1])
    return start


def download_mod_helper(lang, queries, recent):
    """
    A helper function to further extract the phrases from the csv
    :param lang:
    :param queries:
    :param recent:
    :return:
    """
    for query in queries.split(";"):
        if query.strip() != "":
            # query = ast.literal_eval(query)
            query = query.replace("'", "\"")
            pol_contexts = generate_contexts()
            query = query + " is:reply " + pol_contexts
            moderation_tweet_filter = partial(tweet_filter, query)
            download_conversations(topic_string=MODTOPIC2, query_string=query, language=lang,
                                   tweet_filter=moderation_tweet_filter,
                                   recent=recent)
