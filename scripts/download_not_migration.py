import json

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


def run():
    # create topic
    topic_example = TwTopic()
    topic_example.title = "NOT_migration"
    new_topic_dict = topic_example.__dict__
    topic, created = TwTopic.objects.get_or_create(new_topic_dict)

    # create query string with well known migration organisations and their twitter accounts
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
    pp = pprint.PrettyPrinter(indent=4)

    # query_string = ""
    # for (institution in addresses.institutions):
    #    query_string+= institution.twitter_account
    # institutions = list(map(lambda x: list(x.values())[0], addresses.institutions))
    institutions = addresses.institutions
    institutions = filter(lambda x: x.get('institution').get('migration') == 'false', institutions)
    twitter_accounts = map(lambda x: x.get('institution').get('twitter_account').replace("@", ""), institutions)
    twitter_accounts_query_1 = map(lambda x: "(from:{}) OR ".format(x), twitter_accounts)
    twitter_accounts_query_2 = reduce(lambda x, y: x + y, twitter_accounts_query_1)
    twitter_accounts_query_2 = twitter_accounts_query_2[:len(twitter_accounts_query_2) - 4]  # removes the last or
    pp.pprint(twitter_accounts_query_2)

    params = {'query': '{}'.format(twitter_accounts_query_2), 'max_results': '500'}
    search_url = "https://api.twitter.com/2/tweets/search/all"

    connector = TwitterConnector(1)
    json_result = connector.get_from_twitter(search_url, params, True)
    # print(json.dumps(json_result, indent=4, sort_keys=True))

    twitter_data: list = json_result.get("data")
    for tweet_raw in twitter_data:
        try:
            tweet = Tweet()
            tweet.topic = topic
            tweet.query_string = twitter_accounts_query_2
            tweet.text = tweet_raw.get("text")
            tweet.twitter_id = tweet_raw.get("id")
            tweet.save()
        except IntegrityError:
            pass
