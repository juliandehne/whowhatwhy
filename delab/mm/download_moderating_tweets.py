import csv
from functools import partial

from delab.corpus.download_conversations import download_conversations
from delab.delab_enums import LANGUAGE
from delab.models import Tweet, ModerationCandidate2, TwTopic, SimpleRequest

TOPIC = "moderation_mining_2"


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
        title=TOPIC
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
        keywords = query.replace("(", "").replace(")", "").replace("-", "")
        contained = True
        for item in keywords.split(" "):
            if item in tweet.text:
                contained = contained and True
            else:
                contained = False
        if contained:
            ModerationCandidate2.objects.get_or_create(
                tweet=tweet
            )

    except Exception as ex:
        print(ex)
    return tweet


def download_mod_tweets_for_language(reader, lang, recent):
    for row in reader:
        if lang == LANGUAGE.ENGLISH:
            queries = row[8]
            download_mod_helper(lang, queries, recent)
        else:
            if lang == LANGUAGE.GERMAN:
                queries = row[9]
                download_mod_helper(lang, queries, recent)


def download_mod_helper(lang, queries, recent):
    for query in queries.split(";"):
        if query.strip() != "":
            moderation_tweet_filter = partial(tweet_filter, query)
            download_conversations(topic_string=TOPIC, query_string=query, language=lang,
                                   tweet_filter=moderation_tweet_filter,
                                   recent=recent)
