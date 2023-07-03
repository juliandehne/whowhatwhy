from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from delab.delab_enums import MODERATION_TYPE
from delab.models import ConversationFlow


class Intervention(models.Model):
    flow = models.ForeignKey(ConversationFlow, on_delete=models.DO_NOTHING,
                             help_text="the sequence of posts to be moderated")
    text = models.TextField(help_text="the text written to try to moderate the discussion up to this point")
    moderation_type = models.TextField(default=MODERATION_TYPE.CONSENSUS_SEEKING, choices=MODERATION_TYPE.choices,
                                       help_text="the type of moderation strategy employed")
    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
