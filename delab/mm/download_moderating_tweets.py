import csv
import os
import time
from pathlib import Path

import yaml
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.utils import IntegrityError

from delab.corpus.download_conversations import download_conversations
from delab.models import Tweet, TWCandidateIntolerance, ModerationCandidate2, TwTopic, SimpleRequest
from delab.delab_enums import LANGUAGE
from delab.toxicity.perspectives import get_client
from util.abusing_lists import batch
from functools import partial

TOPIC = "moderation_mining_2"


def download_mod_tweets():
    for lang in LANGUAGE:
        with open("delab/mm/FunctionPhrases.csv") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            next(reader, None)  # skip the headers
            download_mod_tweets_for_language(reader, lang)


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
        ModerationCandidate2.objects.get_or_create(
            tweet=tweet
        )
    except Exception as ex:
        print(ex)
    return tweet


def download_mod_tweets_for_language(reader, lang):
    for row in reader:
        if lang == LANGUAGE.ENGLISH:
            queries = row[8]
            download_mod_helper(lang, queries)
        else:
            if lang == LANGUAGE.GERMAN:
                queries = row[9]
                download_mod_helper(lang, queries)


def download_mod_helper(lang, queries):
    for query in queries.split(";"):
        moderation_tweet_filter = partial(tweet_filter, query)
        download_conversations(topic_string=TOPIC, query_string=query, language=lang,
                               tweet_filter=moderation_tweet_filter,
                               recent=True)
