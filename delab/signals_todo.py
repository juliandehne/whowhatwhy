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


# @receiver(post_save, sender=TWCandidate)
def process_candidate_x(sender, instance, created, **kwargs):
    logging.debug("received signal from post_save {} for candidate with pk {}".format(timezone.now(), instance.pk))
    """
    After manually labeling a candidate, a copy needs to be created in order for the secondary or tertiary 
    coder to work    
    """

    candidate_for_second_coder = copy.deepcopy(instance)
    if instance.coded_by is None and instance.coder is not None:
        candidate_for_second_coder.coded_by = instance.coder
        candidate_for_second_coder.coder = None
        candidate_for_second_coder.id = None
        candidate_for_second_coder.pk = None
        candidate_for_second_coder.u_moderator_rating = None
        candidate_for_second_coder.u_sentiment_rating = None
        candidate_for_second_coder.u_author_topic_variance_rating = None
        # candidate_for_second_coder.tweet_id = instance.tweet_id
        candidate_for_second_coder.save()
