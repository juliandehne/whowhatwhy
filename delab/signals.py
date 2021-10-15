import logging

from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.utils import timezone
from django.dispatch import receiver

from delab.models import SimpleRequest, Tweet
from django.db.models.signals import post_save
from delab.tasks import download_conversations_scheduler

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SimpleRequest)
def process_simple_request(sender, instance, created, **kwargs):
    """ After entering the hashtags on the website the query is persisted. Afterwards a twitter call is started to
    download a random conversation.

        Keyword arguments:
        instance -- the title string with space seperated hashtags
    """
    logging.info("received signal from post_save {} for pk {}".format(timezone.now(), instance.pk))

    if created:
        cleaned_hashtags = convert_request_to_hashtag_list(instance.title)
        download_conversations_scheduler(instance.topic.title,
                                         cleaned_hashtags,
                                         simple_request_id=instance.pk,
                                         verbose_name="simple_request_{}".format(instance.pk),
                                         schedule=timezone.now(),
                                         simulate=False, max_data=instance.max_data)


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

