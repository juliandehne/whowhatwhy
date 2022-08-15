# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from delab.delab_enums import PLATFORM, Likert
from delab.models import Tweet


class TWCandidate(models.Model):
    """
    represents the tweets for which a moderation index could be computed.
    This table is also the selector for the manual labeling at the web-interface localhost:8000/delab/label
    """
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    exp_id = models.TextField(default="v0.0.1", help_text="This shows which version of the algorithm is used")
    c_sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    c_author_number_changed_norm = models.FloatField(null=True,
                                                     help_text="the number of different authors posting before and "
                                                               "after the tweet")
    c_author_topic_variance_norm = models.FloatField(null=True,
                                                     help_text="the normalized author diversity")
    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    coded_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="coded_by")
    moderator_index = models.FloatField(
        help_text="a combined measure of the quality of a tweet in terms of moderating value")

    u_moderator_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the tweet is moderating the conversation?")
    u_sentiment_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the tweet expresses a positive sentiment?")
    u_author_topic_variance_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                                         help_text="Do you agree that the tweet has caused a greater "
                                                                   "variety of perspectives?")

    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the platform used (twitter or reddit)")

    class Meta:
        unique_together = ('tweet', 'coder',)

    def get_absolute_url(self):
        return reverse('delab-label-proxy')

    # def save(self, force_insert=False, force_update=False, using=None,
    #         update_fields=None):
    #    super(TWCandidate, self).save(self)
