import logging

from background_task import background

from delab.download_conversations import download_conversations


# from delab.sentiment_training import train_sentiment_classification
# from delab.sentiment_training import classify_tweet_sentiment


# this schedules longer running tasks that are regularly polled by the process task that is started in the background


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
