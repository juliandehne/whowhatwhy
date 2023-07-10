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
    sendable_coder = models.ForeignKey(User, related_name="sendable_coder", on_delete=models.DO_NOTHING, null=True, blank=True)
    sendable = models.BooleanField(null=True, blank=True,
                                   help_text="by checking this button, the moderation will be send out to the given platform")
    sent = models.BooleanField(default=False)


class Classification(models.Model):
    flow = models.ForeignKey(ConversationFlow, on_delete=models.DO_NOTHING,
                             help_text="the sequence of posts to be moderated")
    is_valid_conversation = models.BooleanField(default=True)

    needs_moderation = models.TextField(default=MODERATION_TYPE.CONSENSUS_SEEKING, choices=MODERATION_TYPE.choices,
                                        help_text="the type of moderation strategy needed", null=True, blank=True)

    is_conversation_0 = models.BooleanField(default=False,
                                            help_text="Is this a conversation that can be understood by most people?")
    is_conversation_1 = models.BooleanField(default=False,
                                            help_text="Is there a specific topic or issue being discussed?")
    is_conversation_2 = models.BooleanField(default=False,
                                            help_text="Are there different viewpoints or perspectives being presented?")
    is_conversation_3 = models.BooleanField(default=False,
                                            help_text="Are participants actively questioning or challenging"
                                                      " each other's ideas?")
    is_conversation_4 = models.BooleanField(default=False, help_text="Is this a political debate?")
    is_conversation_5 = models.BooleanField(default=False,
                                            help_text="Are there arguments or counterarguments being presented?")

    agenda_control_1 = models.BooleanField(default=False,
                                           help_text="Are the discussants staying on topic?")
    agenda_control_2 = models.BooleanField(default=False,
                                           help_text="Is there one main topic?")
    agenda_control_3 = models.BooleanField(default=False,
                                           help_text="Is the conversation on a controversial topic?")

    emotion_control_1 = models.BooleanField(default=False,
                                            help_text="Are the discussants showing emotions towards each other?")

    emotion_control_2 = models.BooleanField(default=False,
                                            help_text="Is someone being attacked or insulted?")

    emotion_control_3 = models.BooleanField(default=False,
                                            help_text="Is bad language used?")

    participation_1 = models.BooleanField(default=False,
                                          help_text="Are there many different perspectives?")

    participation_2 = models.BooleanField(default=False,
                                          help_text="Are arguments well formulated and understandable?")

    participation_3 = models.BooleanField(default=False,
                                          help_text="Is the topic very general?")

    consensus_seeking_1 = models.BooleanField(default=False,
                                              help_text="Is the discussion very polarized?")

    consensus_seeking_2 = models.BooleanField(default=False,
                                              help_text="Are they agreeing on things?")

    consensus_seeking_3 = models.BooleanField(default=False,
                                              help_text="Are they talking past each other?")
