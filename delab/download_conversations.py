from django.db import IntegrityError
from twitter.util import TwitterConnector
from twitter.models import Tweet, TwTopic
import logging
from googletrans import Translator
import os
from pathlib import Path
import yaml
import pprint
from functools import reduce
import json


def download_conversations(topic, hashtags):
    logger = logging.getLogger('delab')

    settings_dir = os.path.dirname(__file__)
    project_root = Path(os.path.dirname(settings_dir)).absolute()
    twitter_addresses_yaml = Path.joinpath(project_root, "twitter\\twitter_addresses.yaml")
    with open(twitter_addresses_yaml) as f:
        # use safe_load instead load
        data_map = yaml.safe_load(f)

    class TwitterAddresses:
        def __init__(self, entries):
            self.__dict__.update(entries)

    addresses = TwitterAddresses(data_map)
    #pp = pprint.PrettyPrinter(indent=4)

    twitter_accounts_query_1 = map(lambda x: "(from:{}) OR ".format(x), hashtags)
    twitter_accounts_query_2 = reduce(lambda x, y: x + y, twitter_accounts_query_1)
    twitter_accounts_query_3 = twitter_accounts_query_2[:-4]
    twitter_accounts_query_3 += " lang:en"
    logger.info(twitter_accounts_query_3)

    params = {'query': '{}'.format(twitter_accounts_query_3), 'max_results': '10'}
    search_url = "https://api.twitter.com/2/tweets/search/all"

    connector = TwitterConnector(1)
    json_result = connector.get_from_twitter(search_url, params, True)
    logger.info(json.dumps(json_result, indent=4, sort_keys=True))
    #save_tweets(json_result, topic, twitter_accounts_query_3)


def save_tweets(json_result, topic, query):
    twitter_data: list = json_result.get("data")
    for tweet_raw in twitter_data:
        try:
            tweet = Tweet()
            tweet.topic = topic
            tweet.query_string = query
            tweet.text = tweet_raw.get("text")
            tweet.twitter_id = tweet_raw.get("id")
            tweet.save()
        except IntegrityError:
            pass
