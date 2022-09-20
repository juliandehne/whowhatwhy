# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from delab.delab_enums import Likert
from delab.models import Tweet


class ModerationCandidate2(models.Model):
    """
    represents the tweets which where selected using a dictionary approach.
    This table is also the selector for the manual labeling at the web-interface
    """
    tweet = models.OneToOneField(Tweet, on_delete=models.CASCADE)
    exp_id = models.TextField(default="v0.0.1", help_text="This shows which version of the ditionary was used")
    c_sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    c_author_number_changed_norm = models.FloatField(null=True,
                                                     help_text="the number of different authors posting before and "
                                                               "after the tweet")
    c_author_topic_variance_norm = models.FloatField(null=True,
                                                     help_text="the normalized author diversity")
    moderator_index = models.FloatField(null=True,
                                        help_text="a combined measure of the quality of a tweet in terms of "
                                                  "moderating value")

    u_moderator_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the tweet is moderating the conversation?")
    u_sentiment_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the tweet expresses a positive sentiment?")
    u_author_topic_variance_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                                         help_text="Do you agree that the tweet has caused a greater "
                                                                   "variety of perspectives?")


class ModerationRating(models.Model):
    mod_coder = models.ForeignKey(User, on_delete=models.CASCADE)
    mod_candidate = models.ForeignKey(ModerationCandidate2, on_delete=models.DO_NOTHING)

    u_mod_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                       help_text="Do you agree that parts of the tweet are moderating?")
    u_sis_issues = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                       help_text="Do you agree that the situation before the tweet was issue centered?")
    u_sit_consensus = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                          help_text="Do you agree that the situation before the tweet was consensus "
                                                    "oriented?")
    u_mod_issues = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                       help_text="Do you agree that the moderating tweet tried to focus debating the "
                                                 "issues (non-emotionally)?")
    u_mod_consensus = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                          help_text="Do you agree that the moderating tweet tried to focus support "
                                                    "consensus building?")
    u_clearness_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the meaning of the statement is clear from "
                                                       "the context?")
    u_moderating_part = models.TextField(null=True, blank=True,
                                         help_text="Please copy the part of the tweet that is moderating to here!")

    def get_absolute_url(self):
        return reverse('delab-label-moderation2-proxy')
