# Create your models here.

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
from treenode.models import TreeNodeModel


class ConversationFlow(models.Model):
    image = models.ImageField(default='default.jpg', upload_to='sa_flow_pics')


SIMPLE_REQUEST_VALIDATOR = RegexValidator("(^\#[a-zäöüA-ZÖÄÜ]+(\ \#[a-zA-ZÖÄÜ]+)*$)",
                                          'Please enter hashtags seperated by spaces!')


def validate_exists(title):
    try:
        simple_request = SimpleRequest.objects.filter(title=title).get()
        redirect_url = reverse('delab-conversations-for-request', kwargs={'pk': simple_request.pk})
        # redirect_url = resolve('/conversations/simplerequest/{}'.format(simple_request.pk))
        message_exists = '{} was queried before. Go to <a href="{}"> Result Page </a> to see the results'.format(
            simple_request.title,
            redirect_url)
        raise ValidationError(
            mark_safe(message_exists)
        )
    except ObjectDoesNotExist:
        return True


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


# Create or retrieve a placeholder
def get_sentinel_topic():
    return TwTopic.objects.get_or_create(title="TopicNotGiven")[0].id


class SimpleRequest(models.Model):
    title = models.CharField(max_length=200, validators=[SIMPLE_REQUEST_VALIDATOR, validate_exists])
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING, default=get_sentinel_topic)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('delab-conversations-for-request', kwargs={'pk': self.pk})

    @classmethod
    def create(cls, title):
        simple_request = cls(title=title)
        # do something with the book
        return simple_request


# Create your models here.
class SADictionary(models.Model):
    """ A with json serialized python dictionary that contains the vocabulary for the
        sentiment analysis task that needs to be available at run_time in order to
        process the tweet that is being classified
    """

    dictionary_string = models.TextField()
    title = models.CharField(max_length=200)

    @classmethod
    def create(cls, dictionary_string, title):
        """ creates a template for the saving the dictionary to db

            Parameters
            ----------
            dictionary_string : string
                the serialized python dictionary containing the vocabulary
            title : string
                a string describing what the dictionary is used for i.e. sentiment analysis

            Returns
            -------
            SADictionary
        """
        sa_dictionary = cls(dictionary_string=dictionary_string, title=title)
        # do something with the book
        return sa_dictionary


from django.utils.safestring import mark_safe


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
    sentiment = models.TextField(null=True)  # a shortcut, true is very positive, false is very negative
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
