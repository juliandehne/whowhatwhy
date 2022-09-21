# Create your models here.
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse

from delab.delab_enums import VERSION, PLATFORM, LANGUAGE, Likert, NETWORKRELS, \
    TWEET_RELATIONSHIPS, MODERATION


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


class SimpleRequest(models.Model):
    """
        the idea here is that for a given topic there
        needs to be a query to get a certain part of the twitter conversations from the web.
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
    timeline_bertopic_id = models.IntegerField(null=True, blank=True)
    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the platform used (twitter or reddit)")
    is_moderator = models.BooleanField(default=False)
    follower_downloaded = models.BooleanField(default=False)
    following_downloaded = models.BooleanField(default=False)


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
    conversation_id = models.BigIntegerField()
    simple_request = models.ForeignKey(SimpleRequest, on_delete=models.DO_NOTHING)
    conversation_flow = models.ForeignKey(ConversationFlow, on_delete=models.CASCADE, null=True)
    language = models.TextField(default=LANGUAGE.ENGLISH, choices=LANGUAGE.choices,
                                help_text="the language we are querying")
    bertopic_id = models.IntegerField(null=True,
                                      help_text="the bertopic id given by running a language based bertopic model")
    bert_visual = models.TextField(null=True, blank=True,
                                   help_text="the bertopic representation given by running a language based bertopic "
                                             "model")
    conversation_bertopic_id = models.IntegerField(null=True,
                                                   help_text="the bertopic id given by running a conversation based "
                                                             "bertopic model")
    conversation_bert_visual = models.TextField(null=True, blank=True,
                                                help_text="the bertopic representation given by running a "
                                                          "conversation based bertopic model")
    topic_bertopic_id = models.IntegerField(null=True,
                                            help_text="the bertopic id given by running a delab topic based bertopic "
                                                      "model")
    topic_bert_visual = models.TextField(null=True, blank=True,
                                         help_text="the bertopic representation given by running a delab topic based "
                                                   "bertopic model")

    tn_parent = models.ForeignKey('self', to_field="twitter_id", null=True, on_delete=models.CASCADE,
                                  help_text="This holds the twitter_id (!) of the tweet that was responded to")
    tn_original_parent = models.BigIntegerField(blank=True, null=True)
    tn_parent_type = models.TextField(choices=TWEET_RELATIONSHIPS.choices,
                                      help_text="replied_to, retweeted or quoted", null=True, blank=True)
    c_is_local_moderator = models.BooleanField(null=True,
                                               help_text="True if it is the most moderating tweet in the "
                                                         "conversation, based on m_index")
    c_is_local_moderator_score = models.FloatField(null=True, help_text="m_index without weights")
    h_is_moderator = models.BooleanField(null=True, help_text="True if a human thinks it is moderating")
    h2_is_moderator = models.BooleanField(null=True, help_text="True if a second human thinks it is moderating")

    c_is_moderator = models.BooleanField(null=True,
                                         help_text="True if it is the most moderating tweet in the conversation, "
                                                   "based on moderator-classifier")
    c_is_moderator_score = models.FloatField(null=True, help_text="moderator-classifier trained model applied")

    # objects = DataFrameManager()
    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the plattform used (twitter or reddit)")
    banned_at = models.DateTimeField(null=True)
    d_comment = models.TextField(null=True)
    publish = models.BooleanField(null=True, default=False,
                                  help_text="If this is checked, then the moderation suggestion would actually be "
                                            "send to twitter!")

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
    ft_vector_dump = models.BinaryField(null=True)  # stores the fasttext vectors corresponding to the binary field
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
    u_conflict_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                            help_text="Do you agree that there is a conflict in the sequence?")
    u_conflict_type_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                                 help_text="Do you agree that the conflict is not constructive?")
    u_adversarial_positions_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                                         help_text="Do you agree that the sequence displays opposing "
                                                                   "positions?")
    u_arguments_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the participants offer arguments to support "
                                                       "their positions?")
    u_relationship_focus_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                                      help_text="Do you agree that sequence deals with identity,"
                                                                "relationships, persons, groups or other "
                                                                "non-issue-related aspects?")
    u_relationship_comment = models.TextField(blank=True, null=True,
                                              help_text="If the answers to u_arguments and u_relationship_focus is "
                                                        "not agree, plz comment what the sequence is about")
    u_echo_chamber_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                                help_text="Do you agree that sequence shows aspects of an echo "
                                                          "chamber (repetition, exclusion of other views)?")
    u_whataboutism_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                                help_text="Do you agree that sequence shows whataboutism?")
    u_moderation_type_rating = models.TextField(default=MODERATION.NO_NEED, choices=MODERATION.choices, null=True,
                                                help_text="Which type of moderation would you recommend?")


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
