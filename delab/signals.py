from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from twitter.models import SimpleRequest
from download_conversations import *

@receiver(post_save, sender=SimpleRequest)
def process_simple_request(sender, instance, created, **kwargs):
    if created:
        download_conversations("Proof-of-Concept", instance.split(" "))


