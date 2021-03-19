from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Institution
import logging
from django.contrib import messages


@receiver(post_save, sender=Institution)
def created_institution(sender, instance, created, **kwargs):
    logging.warning('we saved the institution {}'.format(instance))
    # messages.success(instance.request, f'Your account has been updated!')
