import logging

from background_task import background

from delab.data.download_conversations import download_conversations
from delab.sentiment.sentiment_flow_analysis import update_sentiment_flows

# this schedules longer running tasks that are regularly polled by the process task that is started in the background
from delab.models import Tweet
from django.db.models import Q


@background(schedule=1)
def download_conversations_scheduler(topic_string, hashtags, simple_request_id, simulate=True, max_data=False):
    logger = logging.getLogger(__name__)
    """
           TODO:
             - ensure all the downloaded tweets are in the given language
    """
    if simulate:
        logger.error("pretending to downloading conversations{}".format(hashtags))
    else:
        download_conversations(topic_string, hashtags, simple_request_id,max_data=max_data)
        update_sentiments()
        update_sentiment_flows()


def update_sentiments():
    from delab.sentiment.sentiment_classification import classify_tweet_sentiment
    logger = logging.getLogger(__name__)
    logger.info("updating sentiments")
    # importing here to improve server startup time

    tweets = Tweet.objects.filter((Q(sentiment=None) | Q(sentiment_value=None)) & ~Q(sentiment="failed_analysis")).all()
    # tweet_strings = tweets.values_list(["text"], flat=True)
    # print(tweet_strings[1:3])
    tweet_strings = list(map(lambda x: x.text, tweets))
    predictions, sentiments, sentiment_values = classify_tweet_sentiment(tweet_strings)
    for tweet in tweets:
        tweet.sentiment = sentiments.get(tweet.text, "failed_analysis")
        tweet.sentiment_value = sentiment_values.get(tweet.text, None)
        tweet.save()
