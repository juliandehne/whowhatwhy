import logging

from background_task import background

from delab.download_conversations import download_conversations

# this schedules longer running tasks that are regularly polled by the process task that is started in the background
from delab.models import Tweet
from delab.sentiment_classification import classify_tweet_sentiment


@background(schedule=1)
def download_conversations_scheduler(topic_string, hashtags, simple_request_id, simulate=True):
    logger = logging.getLogger(__name__)
    """
           TODO:
             - ensure all the downloaded tweets are in the given language
    """
    if simulate:
        logger.error("pretending to downloading conversations{}".format(hashtags))
    else:
        download_conversations(topic_string, hashtags, simple_request_id)
        # update_sentiments()


def update_sentiments():
    tweets = Tweet.objects.filter(sentiment=None).all()
    #predictions, sentiments = classify_tweet_sentiment(tweets.values_list(["text"], flat=True))
    #for tweet in tweets:
        #tweet.sentiment = sentiments[tweet.text]

    # TODO make this import faster
