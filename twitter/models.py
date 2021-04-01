from django.db import models
from django.db.models import UniqueConstraint

import twitter


# Create your models here.
class TwTopic(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['title'], name="unique_topic_constraint_title"),
        ]


class Tweet(models.Model):
    twitter_id = models.IntegerField()
    text = models.TextField()
    user = models.CharField(max_length=200)
    in_reply_to_status_id = models.IntegerField(null=True)
    in_reply_to_user_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(null=True)
    query_string = models.TextField(null=True)
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['twitter_id'], name="unique_tweet_constraint_id"),
            UniqueConstraint(fields=['text'], name="unique_tweet_constraint_text"),
        ]
