import json
import logging
from functools import reduce

from django.db import IntegrityError
from twitter.models import Tweet, Conversation, TwTopic
from twitter.tw_connection_util import TwitterConnector
from twitter.tw_connection_util import TwitterStreamConnector
from twitter.magic_http_strings import TWEETS_SEARCH_All_URL


def download_conversations(topic_string, hashtags):
    """ This downloads a random twitter conversation with the given hashtags.
        The approach is to use the conversation id and api 2 to get the conversation, for API 1 this workaround
        was possible. https://stackoverflow.com/questions/24791980/is-there-any-work-around-on-fetching-twitter-conversations-using-latest-twitter/24799336

        Keyword arguments:
        topic_string -- the topic of the hashtags
        hashtags -- [hashtag1, hashtag2, ...]
    """
    logger = logging.getLogger(__name__)
    topic, created = TwTopic.objects.get_or_create(
        title=topic_string
    )
    connector = TwitterConnector(1)
    conversation = get_matching_conversation(connector, hashtags, topic, ''.join(hashtags), logger, 10)
    connector = None  # precaution to terminate the thread and the http socket
    # save_tweets(json_result, topic, twitter_accounts_query_3)


def create_topic(topic_string):
    topic_to_save = TwTopic.create(topic_string)
    topic, created = TwTopic.objects.get_or_create(topic_to_save)
    return topic, created


def get_matching_conversation(connector, hashtags, topic, query, logger, max_results, min_results=3):
    """ Helper Function that finds conversation_ids from the hashtags until the criteria are met.

        Keyword arguments:
        hashtags -- the hashtags that constitute the query
        max_results -- the max number of results
        min_results -- the min number of results
    """
    tweets_result = get_tweets_for_hashtags(connector, hashtags, logger, 30)
    candidates = convert_tweet_result_to_list(tweets_result, topic, query, full_tweet=False)
    for candidate in candidates:
        print("selected candidate tweet {}".format(candidate))
        conversation_id = candidate.conversation.conversation_id
        print("conversation_id is {}".format(conversation_id))
        # get the conversation from twitter
        stream_connector = TwitterStreamConnector()

        # TODO add rules
        sample_rules = [
            {"value": "dog has:images", "tag": "dog pictures"},
            {"value": "cat has:images -grumpy", "tag": "cat pictures"},
        ]
        stream_connector.set_rules(sample_rules)
        query = {"tweet.fields": "created_at", "expansions": "author_id", "user.fields": "created_at"}

        # TODO wright partial expression
        checkstream_partial

        stream_connector.get_stream(query, pretty_print_stream)


# TODO write a function that writes a valid conversation to the database after parsing
def check_stream_result_for_valid_conversation(hashtags, topic, min_results, max_results, streaming_result):
    """ The conversation should contain more then one tweet.

        Keyword arguments:
        streaming_result -- the json payload to examine
        hashtags -- a string that represents the original hashtags entered
        topic -- a general TwTopic of the query


        Returns:
        Boolean if valid set was found

        Sideeffects:
        Writes the valid conversation to the db
    """
    pass


def get_tweets_for_hashtags(connector, hashtags, logger, max_results):
    """ downloads the tweets matching the hashtag list.

        Keyword arguments:
        connector -- TwitterConnector
        hashtags -- list of hashtags
        logger -- Logger
        max_results -- the number of max length the conversation should have
    """
    twitter_accounts_query_1 = map(lambda x: "(from:{}) OR ".format(x), hashtags)
    twitter_accounts_query_2 = reduce(lambda x, y: x + y, twitter_accounts_query_1)
    twitter_accounts_query_3 = twitter_accounts_query_2[:-4]
    twitter_accounts_query_3 += " lang:en"
    logger.debug(twitter_accounts_query_3)
    params = {'query': '{}'.format(twitter_accounts_query_3), 'max_results': max_results,
              "tweet.fields": "conversation_id"}

    json_result = connector.get_from_twitter(TWEETS_SEARCH_All_URL, params, True)
    # logger.info(json.dumps(json_result, indent=4, sort_keys=True))
    return json_result


def convert_tweet_result_to_list(tweets_result, topic, query, full_tweet=False, has_conversation_id=True):
    """ converts the raw data to python objects.

        Keyword arguments:
        tweets_result -- the json objeect
        topic -- the TwTopic object
        query -- the used query
        full_tweet -- a flag indicating whether author_id and other specific fields where queried
        has_conversation_id -- a flag if the conversation_id was added as a field
    """
    result_list = []
    twitter_data: list = tweets_result.get("data")
    for tweet_raw in twitter_data:
        tweet = Tweet()
        tweet.topic = topic
        tweet.query_string = query
        tweet.text = tweet_raw.get("text")
        tweet.twitter_id = tweet_raw.get("id")
        if full_tweet:
            tweet.author_id = tweet_raw.get("author_id")
            tweet.created_at = tweet_raw.get("created_at")
        if has_conversation_id:
            conversation = Conversation.create(tweet_raw.get("conversation_id"))
            tweet.conversation = conversation
        result_list.append(tweet)
    return result_list
