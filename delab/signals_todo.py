import logging

from background_task import background

from delab.sentiment.sentiment_training import train_sentiment_classification
from delab.sentiment.sentiment_training import classify_tweet_sentiment


@background(schedule=60)
def train_sentiments(simulate=True):
    logger = logging.getLogger(__name__)
    """ description

            TODO
             - ensure the model is trained only once or per request in the UI
    """
    if simulate:
        logger.info("pretending to calculate sentiments")
    else:
        train_sentiment_classification()


@background(schedule=60)
def calculate_sentiments(tweet_string, simulate=True):
    logger = logging.getLogger(__name__)
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
    if simulate:
        logger.info("pretending to calculate sentiments")
    else:
        classify_tweet_sentiment(tweet_string)
    # update tweet field in db


@background(schedule=60)
def calculate_sentiment_flows(simulate=True):
    logger = logging.getLogger(__name__)
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
    if simulate:
        logger.info("pretending to calculatue sentiment flows")
    else:
        pass