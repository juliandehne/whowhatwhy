# Create your models here.
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse

from delab.delab_enums import VERSION, PLATFORM, LANGUAGE, Likert, NETWORKRELS, \
    TWEET_RELATIONSHIPS, MODERATION, DUOFLOW_METRIC

SIMPLE_REQUEST_VALIDATOR = RegexValidator("(^\#[a-zäöüA-ZÖÄÜ]+(\ \#[a-zA-ZÖÄÜ]+)*$)",
                                          'Please enter hashtags seperated by spaces!')


def validate_exists(title):
    """
    helper function for the interaction with the UI
    This checks if the same query has been sent before
    @param title:
    @return:
    """
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
    """
    TwTopic is a human labeled topic string that is used to group queries
    """
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


class SimpleRequest(models.Model):
    """
        the idea here is that for a given topic
        there needs to be a query to get a certain part of the twitter conversations from the web.
        The title is a string that could be used as a twitter search query
    """

    title = models.CharField(max_length=2000, validators=[validate_exists])
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING, default=get_sentinel_topic,
                              help_text="In case of reddit only the topic will be used as a query and the hot "
                                        "conversations from the subreddit are returned")
    max_data = models.BooleanField(default=False, help_text="This will take the powerset of all the hashtags entered!")
    fast_mode = models.BooleanField(default=False,
                                    help_text="This is for debugging and getting quick results. It will not download "
                                              "the user data!")

    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the platform used (twitter or reddit).  If reddit is selected only the "
                                          "topic will be used to search the related subreddit!")
    version = models.TextField(default=VERSION.v001, choices=VERSION.choices, null=True,
                               help_text="The version of the experiment run.")
    language = models.TextField(default=LANGUAGE.ENGLISH, choices=LANGUAGE.choices,
                                help_text="the language we are querying")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('simple-request-proxy', kwargs={'pk': self.pk})

    @classmethod
    def create(cls, title):
        simple_request = cls(title=title)
        # do something with the book
        return simple_request


from django.utils.safestring import mark_safe


class TweetAuthor(models.Model):
    twitter_id = models.BigIntegerField(unique=True)
    name = models.TextField()
    screen_name = models.TextField()
    location = models.TextField(default="unknown")
    followers_count = models.IntegerField(default=0)
    has_timeline = models.BooleanField(null=True, blank=True)
    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the platform used (twitter or reddit)")
    is_moderator = models.BooleanField(default=False)
    follower_downloaded = models.BooleanField(default=False)
    following_downloaded = models.BooleanField(default=False)
    is_organisation = models.BooleanField(null=True, default=False)
    # is_climate_author = models.BooleanField(default=False)


class Tweet(models.Model):
    twitter_id = models.BigIntegerField(unique=True)
    reddit_id = models.TextField(unique=True, blank=True, null=True)
    text = models.TextField()
    tw_author = models.ForeignKey(TweetAuthor, on_delete=models.DO_NOTHING, null=True)
    author_id = models.BigIntegerField(null=True)
    in_reply_to_status_id = models.BigIntegerField(null=True)
    in_reply_to_user_id = models.BigIntegerField(null=True,
                                                 help_text="The platform internal id of the user of the parent tweet, "
                                                           "i.e. author_id")
    created_at = models.DateTimeField()
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING)
    sentiment_value = models.FloatField(null=True)  # should be mapped between 0 and 1 with 1.0 being very positive
    sentiment = models.TextField(null=True)  # a shortcut, true is very positive, false is very negative
    toxic_value = models.FloatField(null=True)
    is_toxic = models.BooleanField(null=True)
    conversation_id = models.BigIntegerField()
    simple_request = models.ForeignKey(SimpleRequest, on_delete=models.DO_NOTHING)
    language = models.TextField(default=LANGUAGE.ENGLISH, choices=LANGUAGE.choices,
                                help_text="the language we are querying")

    tn_parent = models.ForeignKey('self', to_field="twitter_id", null=True, on_delete=models.CASCADE,
                                  help_text="This holds the twitter_id (!) of the tweet that was responded to")
    tn_original_parent = models.BigIntegerField(blank=True, null=True)
    tn_parent_type = models.TextField(choices=TWEET_RELATIONSHIPS.choices,
                                      help_text="replied_to, retweeted or quoted", null=True, blank=True)

    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the plattform used (twitter or reddit)")
    banned_at = models.DateTimeField(null=True)
    d_comment = models.TextField(null=True)
    publish = models.BooleanField(null=True, default=False,
                                  help_text="If this is checked, then the moderation suggestion would actually be "
                                            "send to twitter!")
    is_climate_author = models.BooleanField(null=True, default=False)
    was_query_candidate = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Tweet'
        verbose_name_plural = 'Tweets'
        unique_together = ('twitter_id', 'platform')

    def __str__(self):
        return "Twitter_ID :{} Conversation_ID:{} Text:{} Autor:{}".format(self.twitter_id,
                                                                           self.conversation_id,
                                                                           self.text,
                                                                           self.author_id)


class Timeline(models.Model):
    """
    represents the twitter timelines of an author (what he has written before)
    """
    author_id = models.BigIntegerField()
    tw_author = models.ForeignKey(TweetAuthor, on_delete=models.DO_NOTHING, null=True, blank=True)
    tweet_id = models.BigIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField()
    conversation_id = models.BigIntegerField(null=True)
    in_reply_to_user_id = models.BigIntegerField(null=True, blank=True)
    lang = models.TextField()
    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the plattform used (twitter or reddit)")

    class Meta:
        unique_together = ('tweet_id', 'platform')


class FollowerNetwork(models.Model):
    source = models.ForeignKey(TweetAuthor, related_name="follower", on_delete=models.DO_NOTHING)
    target = models.ForeignKey(TweetAuthor, related_name="followed", on_delete=models.DO_NOTHING)
    relationship = models.TextField(default=NETWORKRELS.FOLLOWS, choices=NETWORKRELS.choices,
                                    help_text="the kind of relationship, could also be mentions or something else")

    class Meta:
        unique_together = ('source', 'target', 'relationship')


class TweetSequence(models.Model):
    tweets = models.ManyToManyField(Tweet)
    name = models.TextField(blank=True, null=True, unique=True)


class MissingTweets(models.Model):
    twitter_id = models.BigIntegerField(unique=True)
    error_message = models.TextField()
    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the platform used (twitter or reddit)")
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING)
    conversation_id = models.BigIntegerField(null=True, blank=True)
    simple_request = models.ForeignKey(SimpleRequest, on_delete=models.DO_NOTHING)
    url = models.TextField(blank=True, null=True)


class ConversationAuthorMetrics(models.Model):
    conversation_id = models.BigIntegerField()
    author = models.ForeignKey(to=TweetAuthor, on_delete=models.DO_NOTHING)
    centrality = models.FloatField(null=True)
    rb_vision = models.FloatField(null=True)
    baseline_vision = models.FloatField(null=True)
    pb_vision = models.FloatField(null=True)
    n_posts = models.IntegerField()
    is_root_author = models.BooleanField()
    closeness_centrality = models.FloatField(null=True)
    betweenness_centrality = models.FloatField(null=True)
    katz_centrality = models.FloatField(null=True)

    class Meta:
        unique_together = ('conversation_id', 'author')


class ConversationFlowMetrics(models.Model):
    conversation_id = models.BigIntegerField()
    parent = models.ForeignKey(Tweet, related_name="flow_parent", on_delete=models.DO_NOTHING)
    child = models.ForeignKey(Tweet, related_name="flow_child", on_delete=models.DO_NOTHING)
    sentiment_delta = models.FloatField(null=True)
    topic_delta = models.FloatField(null=True)
    author_changed = models.BooleanField(null=True)
    author_timeline_delta = models.FloatField(null=True)
    is_ethos_attack = models.BooleanField(null=True)
    stance = models.FloatField(null=True, help_text="is in opposition -1 or in total agreement with the previous tweet")


class MyImageField(models.ImageField):
    def __str__(self):
        return self.url


class ConversationFlow(models.Model):
    image = MyImageField(default='default.jpg', upload_to='sa_flow_pics')
    tweets = models.ManyToManyField(Tweet)
    flow_name = models.TextField(null=True, unique=True)
    conversation_id = models.BigIntegerField(null=True)
    longest = models.BooleanField(default=False)

    @classmethod
    def create(cls, image, flow_name):
        conversation_flow = cls(image=image, flow_name=flow_name)
        # do something with the book
        return conversation_flow


class Conversation(models.Model):
    """
    TODO at some point change all the other references to conversation_id to Foreign Keys
    """
    conversation_id = models.BigIntegerField(unique=True)
    depth = models.IntegerField()
    branching_factor = models.FloatField()
    root_dominance = models.FloatField()
