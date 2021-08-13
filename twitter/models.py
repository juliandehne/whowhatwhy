from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
from treenode.models import TreeNodeModel
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
from delab.models import ConversationFlow


class TwTopic(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['title'], name="unique_topic_constraint_title"),
        ]

    def __str__(self):
        return self.title

    @classmethod
    def create(cls, title):
        topic = cls(title=title)
        # do something with the book
        return topic


SIMPLE_REQUEST_VALIDATOR = RegexValidator("(^\#[a-zäöüA-ZÖÄÜ]+(\ \#[a-zA-ZÖÄÜ]+)*$)",
                                          'Please enter hashtags seperated by spaces!')


def validate_exists(title):
    try:
        simple_request = SimpleRequest.objects.filter(title=title).get()
        reverse('delab-conversations-for-request', kwargs={'pk': simple_request.pk})
    except ObjectDoesNotExist:
        return True


class SimpleRequest(models.Model):
    title = models.CharField(max_length=200, validators=[SIMPLE_REQUEST_VALIDATOR, validate_exists])
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['title'], name="unique_simple_request_constraint_title"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('delab-conversations-for-request', kwargs={'pk': self.pk})

    @classmethod
    def create(cls, title):
        simple_request = cls(title=title)
        # do something with the book
        return simple_request


class Tweet(TreeNodeModel):
    treenode_display_field = 'text'

    twitter_id = models.IntegerField()
    text = models.TextField()
    author_id = models.IntegerField()
    in_reply_to_status_id = models.IntegerField(null=True)
    in_reply_to_user_id = models.IntegerField(null=True)
    created_at = models.DateTimeField()
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING)
    sentiment_value = models.FloatField(null=True)  # should be mapped between 0 and 1 with 1.0 being very positive
    sentiment = models.BooleanField(null=True)  # a shortcut, true is very positive, false is very negative
    conversation_id = models.IntegerField()
    simple_request = models.ForeignKey(SimpleRequest, on_delete=models.DO_NOTHING)
    conversation_flow = models.ForeignKey(ConversationFlow, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Tweet'
        verbose_name_plural = 'Tweets'

    def __str__(self):
        return "Twitter_ID :{} Conversation_ID:{} Text:{} Autor:{}".format(self.twitter_id,
                                                                           self.conversation_id,
                                                                           self.text,
                                                                           self.author_id)

    @classmethod
    def create(cls, topic, text, simple_request, twitter_id, author_id, conversation_id, sentiment_value=0,
               sentiment=False,
               parent=None, priority=0):
        tweet = cls(topic=topic,
                    text=text,
                    twitter_id=twitter_id,
                    author_id=author_id,
                    simple_request=simple_request,
                    conversation_id=conversation_id,
                    sentiment_value=sentiment_value,
                    sentiment=sentiment,
                    tn_parent=parent,
                    tn_priority=priority)
        return tweet
