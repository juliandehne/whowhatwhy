# Create your models here.

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
from django_pandas.managers import DataFrameManager
from treenode.models import TreeNodeModel


class ConversationFlow(models.Model):
    image = models.ImageField(default='default.jpg', upload_to='sa_flow_pics')

    @classmethod
    def create(cls, image):
        conversation_flow = cls(image=image)
        # do something with the book
        return conversation_flow


SIMPLE_REQUEST_VALIDATOR = RegexValidator("(^\#[a-zäöüA-ZÖÄÜ]+(\ \#[a-zA-ZÖÄÜ]+)*$)",
                                          'Please enter hashtags seperated by spaces!')


def validate_exists(title):
    try:
        simple_request = SimpleRequest.objects.filter(title=title).get()
        redirect_url = reverse('simple-request-proxy', kwargs={'pk': simple_request.pk})
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

    def get_absolute_url(self):
        return reverse('delab-create-simple-request')

    @classmethod
    def create(cls, title):
        topic = cls(title=title)
        # do something with the book
        return topic


# Create or retrieve a placeholder
def get_sentinel_topic():
    return TwTopic.objects.get_or_create(title="TopicNotGiven")[0].id


'''
    the idea here is that for a given topic there 
    needs to be a series of hashtags to get a certain part of the twitter conversations from the web.
    The title is a string that could be used as a twitter search query
'''


class SimpleRequest(models.Model):
    title = models.CharField(max_length=2000, validators=[SIMPLE_REQUEST_VALIDATOR, validate_exists])
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING, default=get_sentinel_topic)
    max_data = models.BooleanField(default=False, help_text="This will take the powerset of all the hashtags entered!")
    fast_mode = models.BooleanField(default=False,
                                    help_text="This is for debugging and getting quick results. It will not download the user data!")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('simple-request-proxy', kwargs={'pk': self.pk})

    @classmethod
    def create(cls, title):
        simple_request = cls(title=title)
        # do something with the book
        return simple_request


class TopicDictionary(models.Model):
    """
    This contains the pickled Vocabulary for the Topic Distances
    """
    word = models.CharField(max_length=200, unique=True)  # the word that needs embedding
    ft_vector = models.TextField()  # the json serialized fasttext vector


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


class TweetAuthor(models.Model):
    twitter_id = models.BigIntegerField(unique=True)
    name = models.TextField()
    screen_name = models.TextField()
    location = models.TextField(default="unknown")
    followers_count = models.IntegerField(default=0)
    has_timeline = models.BooleanField(null=True, blank=True)


class Tweet(models.Model):
    treenode_display_field = 'text'
    twitter_id = models.BigIntegerField(unique=True)
    text = models.TextField()
    tw_author = models.ForeignKey(TweetAuthor, on_delete=models.DO_NOTHING, null=True)
    author_id = models.BigIntegerField(null=True)
    in_reply_to_status_id = models.BigIntegerField(null=True)
    in_reply_to_user_id = models.BigIntegerField(null=True)
    created_at = models.DateTimeField()
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING)
    sentiment_value = models.FloatField(null=True)  # should be mapped between 0 and 1 with 1.0 being very positive
    sentiment = models.TextField(null=True)  # a shortcut, true is very positive, false is very negative
    conversation_id = models.BigIntegerField()
    simple_request = models.ForeignKey(SimpleRequest, on_delete=models.DO_NOTHING)
    conversation_flow = models.ForeignKey(ConversationFlow, on_delete=models.CASCADE, null=True)
    language = models.TextField(default="unk")
    bertopic_id = models.IntegerField(null=True)
    bert_visual = models.TextField(null=True, blank=True)
    tn_parent = models.BigIntegerField(null=True)
    c_is_local_moderator = models.BooleanField(null=True,
                                               help_text="True if it is the most moderating tweet in the conversation, based on m_index")
    c_is_local_moderator_score = models.FloatField(null=True, help_text="m_index without weights")
    h_is_moderator = models.BooleanField(null=True, help_text="True if a human thinks it is moderating")
    h2_is_moderator = models.BooleanField(null=True, help_text="True if a second human thinks it is moderating")

    c_is_moderator = models.BooleanField(null=True,
                                         help_text="True if it is the most moderating tweet in the conversation, based on moderator-classifier")
    c_is_moderator_score = models.FloatField(null=True, help_text="moderator-classifier trained model applied")

    # objects = DataFrameManager()

    class Meta:
        verbose_name = 'Tweet'
        verbose_name_plural = 'Tweets'

    def __str__(self):
        return "Twitter_ID :{} Conversation_ID:{} Text:{} Autor:{}".format(self.twitter_id,
                                                                           self.conversation_id,
                                                                           self.text,
                                                                           self.author_id)


class Timeline(models.Model):
    author_id = models.BigIntegerField()
    tw_author = models.ForeignKey(TweetAuthor, on_delete=models.DO_NOTHING, null=True, blank=True)
    tweet_id = models.BigIntegerField(unique=True)
    text = models.TextField()
    created_at = models.DateTimeField()
    conversation_id = models.BigIntegerField(null=True)
    in_reply_to_user_id = models.BigIntegerField(null=True, blank=True)
    lang = models.TextField()
    ft_vector_dump = models.BinaryField(null=True)  # stores the fasttext vectors corresponding to the binary field
