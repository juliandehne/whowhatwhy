import json
import logging
from functools import reduce
from django.db import IntegrityError
from twitter.models import Tweet
from twitter.util import TwitterConnector
from twitter.magic_strings import SEARCH_ALL_URL


def download_conversations(topic, hashtags):
    """ This downloads a random twitter conversation with the given hashtags.

        Keyword arguments:
        arg1 -- the topic of the hashtags
        arg2 -- [hashtag1, hashtag2, ...]
    """
    logger = logging.getLogger(__name__)
    get_matching_conversation_id(hashtags, logger, 10)
    # save_tweets(json_result, topic, twitter_accounts_query_3)


def get_tweets_for_hashtags(hashtags, logger, max_results):
    twitter_accounts_query_1 = map(lambda x: "(from:{}) OR ".format(x), hashtags)
    twitter_accounts_query_2 = reduce(lambda x, y: x + y, twitter_accounts_query_1)
    twitter_accounts_query_3 = twitter_accounts_query_2[:-4]
    twitter_accounts_query_3 += " lang:en"
    logger.debug(twitter_accounts_query_3)
    params = {'query': '{}'.format(twitter_accounts_query_3), 'max_results': max_results, "tweet.fields": "conversation_id"}
    connector = TwitterConnector(1)
    json_result = connector.get_from_twitter(SEARCH_ALL_URL, params, True)
    # logger.info(json.dumps(json_result, indent=4, sort_keys=True))
    return json_result


def get_matching_conversation_id(hashtags, logger, max_results):
    conversation = []
    while len(conversation) < 6:
        tweets_result = get_tweets_for_hashtags(hashtags, logger, 10)
        conversation_id = tweets_result.get("data")[0].get("conversation_id")
        print("conversation_id is {}".format(conversation_id))
        # get the conversation from twitter
        conversation_query = "conversation_id:{}".format(conversation_id)
        params = {'query': '{}'.format(conversation_query), 'max_results': max_results}
        connector = TwitterConnector(1)
        json_result = connector.get_from_twitter(SEARCH_ALL_URL, params, True)
        logger.info(json.dumps(json_result, indent=4, sort_keys=True))
        # TODO finish the code and implement download the whole conversation
        break
        # get_conversation_for_id()
    pass




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
