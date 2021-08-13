import logging

from background_task import background

from delab.download_conversations import download_conversations
from delab.sentiment_training import train_sentiment_classification
from delab.sentiment_training import classify_tweet_sentiment

# this schedules longer running tasks that are regularly polled by the process task that is started in the background
logger = logging.getLogger(__name__)


@background(schedule=60)
def download_conversations_scheduler(topic, hashtags, simple_request, simulate=False):
    """
           TODO:
             - ensure all the downloaded tweets are in the given language
    """
    if simulate:
        logger.info("pretending to downloading conversations")
    else:
        download_conversations(topic, hashtags, simple_request)


@background(schedule=60)
def train_sentiments():
    """ description

            TODO
             - ensure the model is trained only once or per request in the UI
    """
    train_sentiment_classification()


@background(schedule=60)
def calculate_sentiments(tweet_string):
    """ description

        TODO:
          - make sure the file system is not opened for every tweet
          - update the tweet sentiment fields
          - find out the exactly meaning of the weights and scale between 0 and 1

        Parameters
        ----------
        tweet_string : str
            the tweet to classify

    """
    classify_tweet_sentiment(tweet_string)
    # update tweet field in db


@background(schedule=60)
def calculate_sentiment_flows():
    """ computes the "gleitenden Mittelwert" for the conversations
        and determines tweets that escalated the sentiments by
        looking at the derivation (which is the max of the difference in a discrete setting like this)

        Parameters
        ----------
        param 1 : type
            [optional] description
        param 2 : type
            [optional] description

        Returns
        -------
        type
            description
    """
    pass
