import datetime

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from twitter.models import SimpleRequest
from twitter.tasks import download_conversations_scheduler
from django.shortcuts import redirect


@receiver(post_save, sender=SimpleRequest)
def process_simple_request(sender, instance, created, **kwargs):
    """ After entering the hashtags on the website the query is persisted. Afterwards a twitter call is started to
    download a random conversation.

        Keyword arguments:
        instance -- the title string with space seperated hashtags
    """

    if created:
        cleaned_hashtags = []
        hashtags = instance.title.split(" ")
        for hashtag in hashtags:
            cleaned_hashtags.append(hashtag[1:])  # removes the # symbol
        download_conversations_scheduler("Proof-of-Concept", cleaned_hashtags, simple_request=instance,
                                         schedule=timezone.now(), simulate=True)
