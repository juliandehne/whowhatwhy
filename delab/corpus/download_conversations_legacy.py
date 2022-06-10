from delab.models import Tweet


def convert_tweet_result_to_list(tweets_result, topic, full_tweet=False, has_conversation_id=True):
    """ converts the raw data to python objects.

        Keyword arguments:
        tweets_result -- the json object
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

