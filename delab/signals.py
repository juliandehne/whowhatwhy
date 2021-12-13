import copy
import logging

from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.utils import timezone
from django.dispatch import receiver

from delab.models import SimpleRequest, Tweet, TWCandidate, PLATFORM
from django.db.models.signals import post_save
from delab.tasks import download_conversations_scheduler
from delab.bot.sender import publish_moderation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tweet)
def process_moderation(sender, instance, created, **kwargs):
    if instance.platform == PLATFORM.DELAB and instance.publish:
        publish_moderation(instance)


# @receiver(post_save, sender=TWCandidate)
def process_candidate(sender, instance, created, **kwargs):
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


@receiver(post_save, sender=SimpleRequest)
def process_simple_request(sender, instance, created, **kwargs):
    """ After entering the hashtags on the website the query is persisted. Afterwards a twitter call is started to
    download a random conversation.

        Keyword arguments:
        instance -- the title string with space seperated hashtags
    """
    logging.info("received signal from post_save {} for pk {}".format(timezone.now(), instance.pk))

    if created:
        # cleaned_hashtags = convert_request_to_hashtag_list(instance.title)
        download_conversations_scheduler(instance.topic.title,
                                         instance.platform,
                                         instance.title,
                                         simple_request_id=instance.pk,
                                         verbose_name="simple_request_{}".format(instance.pk),
                                         schedule=timezone.now(),
                                         simulate=False, max_data=instance.max_data,
                                         fast_mode=instance.fast_mode, language=instance.language)


def convert_request_to_hashtag_list(title):
    """ description

        Parameters
        ----------
        title : str
            i.e. "#covid #vaccination"
        Returns
        -------
        [str]
            i.e. [covid, vaccination]
    """
    cleaned_hashtags = []
    if ' ' in title:
        hashtags = title.split(" ")
        for hashtag in hashtags:
            cleaned_hashtags.append(hashtag[1:])  # removes the # symbol
    else:
        cleaned_hashtags.append(title[1:])

    return cleaned_hashtags
