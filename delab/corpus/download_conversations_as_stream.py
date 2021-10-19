import json
from functools import reduce, partial

from delab.tw_connection_util import TwitterStreamConnector


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
