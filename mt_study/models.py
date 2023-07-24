from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from delab.delab_enums import MODERATION_TYPE
from delab.models import ConversationFlow


def validate_insert_position(value, instance=None):
    if instance:
        sequence_length = len(instance.flow.tweets.all())
        # Access the instance and perform validation logic
        # For example, you can access other fields of the instance
        if sequence_length < value or value == 0:
            raise ValidationError("The position cannot be greater than the number of posts and must be bigger than 0.")
    else:
        # Handle the case when the instance is not available
        raise ValidationError("Validation failed. No instance found.")


class Intervention(models.Model):
    flow = models.ForeignKey(ConversationFlow, on_delete=models.DO_NOTHING,
                             help_text="the sequence of posts to be moderated")
    text = models.TextField(help_text="the text written to try to moderate the discussion up to this point")
    moderation_type = models.TextField(default=MODERATION_TYPE.CONSENSUS_SEEKING, choices=MODERATION_TYPE.choices,
                                       help_text="the type of moderation strategy employed")
    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    sendable_coder = models.ForeignKey(User, related_name="sendable_coder", on_delete=models.DO_NOTHING, null=True,
                                       blank=True)
    sendable = models.BooleanField(null=True, blank=True,
                                   help_text="by checking this button, the moderation will be send out to the given platform")
    sent = models.BooleanField(default=False)

    position_in_flow = models.IntegerField(default=-1, help_text="-1 for end of flow. 1 for after the first post etc.",
                                           )


class Classification(models.Model):
    flow = models.ForeignKey(ConversationFlow, on_delete=models.DO_NOTHING,
                             help_text="the sequence of posts to be moderated")

    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_conversation_0 = models.BooleanField(default=True,
                                            help_text="Is this a conversation that can be understood by most people?")
    is_conversation_1 = models.BooleanField(default=True,
                                            help_text="Is there a specific topic or issue being discussed?")
    is_conversation_2 = models.BooleanField(default=True,
                                            help_text="Are there different viewpoints or perspectives being presented?")
    is_conversation_3 = models.BooleanField(default=True,
                                            help_text="Are participants actively questioning or challenging"
                                                      " each other's ideas?")
    is_conversation_4 = models.BooleanField(default=False, help_text="Is this a political debate? If unsure mark no.")
    is_conversation_5 = models.BooleanField(default=True,
                                            help_text="Are there arguments or counterarguments being presented?")

    agenda_control_1 = models.BooleanField(default=True,
                                           help_text="Are the discussants staying on topic?")
    agenda_control_2 = models.BooleanField(default=False,
                                           help_text="Is it hard to keep track of the issue at hand?")
    agenda_control_3 = models.BooleanField(default=False,
                                           help_text="Is the conversation split in two or more very separate topics?")

    emotion_control_1 = models.BooleanField(default=False,
                                            help_text="Are the discussants showing emotions towards each other?")

    emotion_control_2 = models.BooleanField(default=False,
                                            help_text="Is someone being attacked or insulted?")

    emotion_control_3 = models.BooleanField(default=False,
                                            help_text="Is bad language used?")

    participation_1 = models.BooleanField(default=True,
                                          help_text="Are there many different perspectives (allowed)?")

    participation_2 = models.BooleanField(default=False,
                                          help_text="Is the discussion dominated by a certain group?")

    # Are arguments well formulated and understandable?
    participation_3 = models.BooleanField(default=True,
                                          help_text="Is this a discussion where everyone can join in?")

    consensus_seeking_1 = models.BooleanField(default=False,
                                              help_text="Is the discussion very polarized?")

    consensus_seeking_2 = models.BooleanField(default=True,
                                              help_text="Are the discussants agreeing on things?")

    consensus_seeking_3 = models.BooleanField(default=False,
                                              help_text="Are they talking past each other?")

    norm_control_1 = models.BooleanField(default=False,
                                         help_text="Are there some intolerant speech acts in the conversation?")
    norm_control_2 = models.BooleanField(default=False,
                                         help_text="Are the discussants violating some basic social rules?")
    norm_control_3 = models.BooleanField(default=False,
                                         help_text="Are there comments that are racist, sexist, antisemitic or similar?")

    elaboration_support_1 = models.BooleanField(default=True,
                                                help_text="Are arguments well formulated and understandable?")
    elaboration_support_2 = models.BooleanField(default=False,
                                                help_text="Are there hidden assumptions that shape the discussion?")
    elaboration_support_3 = models.BooleanField(default=False,
                                                help_text="Is there a tabu involved (elefant in the room)"
                                                          " that needs to be addressed to further the conversation?")

    is_valid_conversation = models.BooleanField(default=True, help_text="Mark this,"
                                                                        " if the conversation is correct in a technical sense "
                                                                        "(no weird letters, deleted posts or similar!")

    needs_moderation = models.TextField(choices=MODERATION_TYPE.choices,
                                        help_text="The type of moderation strategy needed", null=True, blank=True)

