import json
import logging
from functools import reduce

import requests
from django.db import IntegrityError

from twitter.TwConversationTree import TreeNode
from twitter.models import Tweet, TwTopic, SimpleRequest
from twitter.tw_connection_util import TwitterConnector
from twitter.tw_connection_util import TwitterStreamConnector
from twitter.magic_http_strings import TWEETS_SEARCH_All_URL
from twitter.tw_connection_util import TwitterAPIWrapper
from functools import partial

from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, TwitterPager
import pandas as pd


def download_conversations(topic_string, hashtags):
    """ This downloads a random twitter conversation with the given hashtags.
        The approach is similar to https://cborchers.com/2021/03/23/notes-on-downloading-conversations-through-twitters-v2-api/
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

    request_string = ''.join(hashtags)
    simple_request, created = SimpleRequest.objects.get_or_create(
        title=request_string
    )

    connector = TwitterConnector(1)
    get_matching_conversation(connector, hashtags, topic, simple_request, logger)

    connector = None  # precaution to terminate the thread and the http socket
    # save_tweets(json_result, topic, twitter_accounts_query_3)


def create_topic(topic_string):
    topic_to_save = TwTopic.create(topic_string)
    topic, created = TwTopic.objects.get_or_create(topic_to_save)
    return topic, created


def save_tree_to_db(root_node, topic, simple_request, conversation_id, parent=None, priority=0):
    tweet, created = Tweet.objects.get_or_create(
        topic=topic,
        text=root_node.data["text"],
        simple_request=simple_request,
        twitter_id=root_node.data["id"],
        author_id=root_node.data["author_id"],
        conversation_id=conversation_id,
        in_reply_to_user_id=root_node.data.get("in_reply_to_user_id", None),
        in_reply_to_status_id=root_node.data.get("in_reply_to_status_id", None),
        tn_parent=parent,
        tn_priority=priority
    )

    if not len(root_node.children) == 0:
        for child in root_node.children:
            save_tree_to_db(child, topic, simple_request, conversation_id, tweet)


def get_matching_conversation(connector, hashtags, topic, simple_request, logger,
                              max_conversation_length=1000,
                              min_conversation_length=10,
                              language="lang:en",
                              max_number_of_candidates=300):
    """ Helper Function that finds conversation_ids from the hashtags until the criteria are met.

        Keyword arguments:
        hashtags -- the hashtags that constitute the query
        max_results -- the max number of results
        min_results -- the min number of results
    """
    tweets_result = get_tweets_for_hashtags(connector, hashtags, logger, max_number_of_candidates, language)
    candidates = convert_tweet_result_to_list(tweets_result, topic, full_tweet=False)
    # deal_with_conversation_candidates_as_stream(candidates, hashtags, language, topic, min_results, max_results)
    for candidate in candidates:
        logger.info("selected candidate tweet {}".format(candidate))
        candidate_id = candidate.conversation_id
        try:
            root_node = retrieve_replies(candidate_id)
        except requests.exceptions.Timeout:
            print("Timeout occurred")
        if root_node is None:
            logger.error("found conversation_id that could not be processed")
            continue
        else:
            flat_tree_size = root_node.flat_size()
            logger.info("retrieved node with number of children: {}".format(flat_tree_size))
        if min_conversation_length < flat_tree_size < max_conversation_length:
            save_tree_to_db(root_node, topic, simple_request, candidate_id)
            print("found suitable conversation and saved to db {}".format(candidate_id))
            root_node.print_tree(0)


def retrieve_replies(conversation_id):
    """
    follows the tutorial from here https://towardsdatascience.com/mining-replies-to-tweets-a-walkthrough-9a936602c4d6

    Retrieves level 1 replies for a given conversation id
    Returns lists conv_id, child_id, text tuple which shows every reply's tweet_id and text in the last two lists

    """

    twapi = TwitterAPIWrapper.get_twitter_API()
    root = None

    try:
        # GET ROOT OF THE CONVERSATION
        r = twapi.request(f'tweets/:{conversation_id}',
                          {
                              'tweet.fields': 'author_id,conversation_id,created_at,in_reply_to_user_id'
                          })

        for item in r:
            root = TreeNode(item)
            # print(f'ROOT {root.id()}')

        # GET ALL REPLIES IN CONVERSATION

        pager = TwitterPager(twapi, 'tweets/search/recent',
                             {
                                 'query': f'conversation_id:{conversation_id}',
                                 'tweet.fields': 'author_id,conversation_id,created_at,in_reply_to_user_id'
                             })
        orphans = []

        for item in pager.get_iterator(wait=2):
            node = TreeNode(item)
            # print(f'{node.id()} => {node.reply_to()}')
            # COLLECT ANY ORPHANS THAT ARE NODE'S CHILD
            orphans = [orphan for orphan in orphans if not node.find_parent_of(orphan)]
            # IF NODE CANNOT BE PLACED IN TREE, ORPHAN IT UNTIL ITS PARENT IS FOUND
            if not root.find_parent_of(node):
                orphans.append(node)

        conv_id, child_id, text = root.list_l1()
        #         print('\nTREE...')
        # 	    root.print_tree(0)

        assert len(orphans) == 0, f'{len(orphans)} orphaned tweets'

    except TwitterRequestError as e:
        print(e.status_code)
        for msg in iter(e):
            print(msg)

    except TwitterConnectionError as e:
        print(e)

    except Exception as e:
        print(e)

    return root


def reply_thread_maker(conv_ids):
    """
    Retrieves replies for a list of conversation ids (conv_ids
    Returns a dataframe with columns [conv_id, child_id, text] tuple which shows every reply's tweet_id and text in the last two columns
    """

    conv_id = []
    child_id = []
    text = []
    for id in conv_ids:
        conv_id1, child_id1, text1 = retrieve_replies(id)
        conv_id.extend(conv_id1)
        child_id.extend(child_id1)
        text.extend(text1)

    replies_data = {'conversation_id': conv_id,
                    'child_tweet_id': child_id,
                    'tweet_text': text}

    replies = pd.DataFrame(replies_data)
    return replies


def deal_with_conversation_candidates_as_stream(candidates, hashtags, language, topic, min_results,
                                                max_results):
    """ The idea of this function is to user the filtered stream api to get real time data to a conversation
        and also leverage the sentiment analysis build in

        {
            "value": "#something -horrible -worst -sucks -bad -disappointing",
            "tag": "#something positive"
        },
        {
            "value": "#something -happy -exciting -excited -favorite -fav -amazing -lovely -incredible",
            "tag": "#something negative"
        }

        Keyword arguments:
        arg1 -- description
        arg2 -- description
    """

    stream_connector = TwitterStreamConnector()
    existing_rules = stream_connector.get_rules()
    stream_connector.delete_all_rules(existing_rules)
    for candidate in candidates:
        print("selected candidate tweet {}".format(candidate))
        conversation_id = candidate.conversation.conversation_id
        # get the conversation from twitter

        # {"value": "cat has:images -grumpy", "tag": "cat pictures"},
        rules = [{"value": "conversation_id:{}".format(conversation_id)}]
        # create hashtagsrule
        hashtag_query_1 = map(lambda x: "#{} OR ".format(x), hashtags)
        hashtag_query_2 = reduce(lambda x, y: x + y, hashtag_query_1)
        hashtag_query_3 = " (" + hashtag_query_2[:-4] + " " + language + ")"
        print("looking up conversation for original query:{}".format(hashtag_query_3))

        # rules = [{"value": "conversation_id:{}".format(conversation_id), "tag": "conversationid{}".format(conversation_id)}]
        rules = [{"value": hashtag_query_3, "tag": "matching tags {}".format(hashtags)}]
        # TODO fix the problem that the conversation is not returned for the conversation rule

        print("Rules used are{}".format(rules))
        stream_connector.set_rules(rules)

        query = {"tweet.fields": "created_at,in_reply_to_user_id,lang,referenced_tweets", "expansions": "author_id"}
        # query = {"tweet.fields": "created_at,in_reply_to_user_id,lang,referenced_tweets", "expansions":
        # "author_id", "user.fields": "created_at"}

        '''
        this creates prefills the function with the needed params in order to have the function fit the signature in the
        stream delegate
        '''
        p_check_function = partial(check_stream_result_for_valid_conversation, hashtags, topic, min_results,
                                   max_results, conversation_id)

        stream_connector.get_stream(query, p_check_function)

        existing_rules = stream_connector.get_rules()
        stream_connector.delete_all_rules(existing_rules)


# TODO write a function that writes a valid conversation to the database after parsing
def check_stream_result_for_valid_conversation(hashtags, topic, min_results, max_results, conversation_id,
                                               streaming_result):
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

    # TODO implement

    if "data" not in streaming_result:
        return False

    print("Streaming RESULT for conversation:{}\n".format(conversation_id) + json.dumps(streaming_result.get("data"),
                                                                                        indent=4,
                                                                                        sort_keys=True))
    return True


def get_tweets_for_hashtags(connector, hashtags, logger, max_results, language="lang:en"):
    """ downloads the tweets matching the hashtag list.
        using https://api.twitter.com/2/tweets/search/all

        Keyword arguments:
        connector -- TwitterConnector
        hashtags -- list of hashtags
        logger -- Logger
        max_results -- the number of max length the conversation should have
    """
    twitter_accounts_query_1 = map(lambda x: "(from:{}) OR ".format(x), hashtags)
    twitter_accounts_query_2 = reduce(lambda x, y: x + y, twitter_accounts_query_1)
    twitter_accounts_query_3 = twitter_accounts_query_2[:-4]
    twitter_accounts_query_3 += " " + language
    logger.debug(twitter_accounts_query_3)
    params = {'query': '{}'.format(twitter_accounts_query_3), 'max_results': max_results,
              "tweet.fields": "conversation_id,author_id"}

    json_result = connector.get_from_twitter(TWEETS_SEARCH_All_URL, params, True)
    # logger.info(json.dumps(json_result, indent=4, sort_keys=True))
    return json_result


def convert_tweet_result_to_list(tweets_result, topic, full_tweet=False, has_conversation_id=True):
    """ converts the raw data to python objects.

        Keyword arguments:
        tweets_result -- the json objeect
        topic -- the TwTopic object
        query -- the used query
        full_tweet -- a flag indicating whether author_id and other specific fields where queried
        has_conversation_id -- a flag if the conversation_id was added as a field

        returns [Tweet]
    """
    result_list = []
    if "data" not in tweets_result:
        return result_list
    else:
        twitter_data: list = tweets_result.get("data")
        for tweet_raw in twitter_data:
            tweet = Tweet()
            tweet.topic = topic
            tweet.text = tweet_raw.get("text")
            tweet.twitter_id = tweet_raw.get("id")
            if full_tweet:
                tweet.author_id = tweet_raw.get("author_id")
                tweet.created_at = tweet_raw.get("created_at")
            if has_conversation_id:
                tweet.conversation_id = tweet_raw.get("conversation_id")
            result_list.append(tweet)
    return result_list
