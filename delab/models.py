# Create your models here.
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
from treenode.models import TreeNodeModel

from delab.delab_enums import VERSION, PLATFORM, LANGUAGE, Likert, INTOLERANCE, STRATEGIES, NETWORKRELS, \
    TWEET_RELATIONSHIPS


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
    title = models.CharField(max_length=2000, validators=[validate_exists])
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    topic = models.ForeignKey(TwTopic, on_delete=models.DO_NOTHING, default=get_sentinel_topic,
                              help_text="In case of reddit only the topic will be used as a query and the hot conversations from the subreddit are returned")
    max_data = models.BooleanField(default=False, help_text="This will take the powerset of all the hashtags entered!")
    fast_mode = models.BooleanField(default=False,
                                    help_text="This is for debugging and getting quick results. It will not download the user data!")

    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the plattform used (twitter or reddit).  If reddit is selected only the topic will be used to search the related subreddit!")
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
                                help_text="the plattform used (twitter or reddit)")
    is_moderator = models.BooleanField(default=False)


class Tweet(models.Model):
    treenode_display_field = 'text'
    twitter_id = models.BigIntegerField(unique=True)
    text = models.TextField()
    tw_author = models.ForeignKey(TweetAuthor, on_delete=models.DO_NOTHING, null=True)
    author_id = models.BigIntegerField(null=True)
    in_reply_to_status_id = models.BigIntegerField(null=True)
    in_reply_to_user_id = models.BigIntegerField(null=True,
                                                 help_text="The platform internal id of the user of the parent tweet, i.e. author_id")
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
                                   help_text="the bertopic representation given by running a language based bertopic model")
    conversation_bertopic_id = models.IntegerField(null=True,
                                                   help_text="the bertopic id given by running a conversation based bertopic model")
    conversation_bert_visual = models.TextField(null=True, blank=True,
                                                help_text="the bertopic represantation given by running a conversation based bertopic model")
    topic_bertopic_id = models.IntegerField(null=True,
                                            help_text="the bertopic id given by running a delab topic based bertopic model")
    topic_bert_visual = models.TextField(null=True, blank=True,
                                         help_text="the bertopic represantation given by running a delab topic based bertopic model")

    tn_parent = models.ForeignKey('self', to_field="twitter_id", null=True, on_delete=models.DO_NOTHING,
                                  help_text="This holds the twitter_id (!) of the tweet that was responded to")
    tn_parent_type = models.TextField(choices=TWEET_RELATIONSHIPS.choices,
                                      help_text="replied_to, retweeted or quoted", null=True, blank=True)
    c_is_local_moderator = models.BooleanField(null=True,
                                               help_text="True if it is the most moderating tweet in the conversation, based on m_index")
    c_is_local_moderator_score = models.FloatField(null=True, help_text="m_index without weights")
    h_is_moderator = models.BooleanField(null=True, help_text="True if a human thinks it is moderating")
    h2_is_moderator = models.BooleanField(null=True, help_text="True if a second human thinks it is moderating")

    c_is_moderator = models.BooleanField(null=True,
                                         help_text="True if it is the most moderating tweet in the conversation, based on moderator-classifier")
    c_is_moderator_score = models.FloatField(null=True, help_text="moderator-classifier trained model applied")

    # objects = DataFrameManager()
    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the plattform used (twitter or reddit)")
    banned_at = models.DateTimeField(null=True)
    d_comment = models.TextField(null=True)
    publish = models.BooleanField(null=True, default=False,
                                  help_text="If this is checked, then the moderation suggestion would actually be send to twitter!")

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


class TWCandidate(models.Model):
    """
    represents the tweets for which a moderation index could be computed.
    This table is also the selector for the manual labeling at the web-interface localhost:8000/delab/label
    """
    tweet = models.ForeignKey(Tweet, on_delete=models.DO_NOTHING)
    exp_id = models.TextField(default="v0.0.1", help_text="This shows which version of the algorithm is used")
    c_sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    c_author_number_changed_norm = models.FloatField(null=True,
                                                     help_text="the number of different authors posting before and after the tweet")
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
                                                         help_text="Do you agree that the tweet has caused a greater variety of perspectives?")

    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the plattform used (twitter or reddit)")

    class Meta:
        unique_together = ('tweet', 'coder',)

    def get_absolute_url(self):
        return reverse('delab-label-proxy')

    # def save(self, force_insert=False, force_update=False, using=None,
    #         update_fields=None):
    #    super(TWCandidate, self).save(self)


class UkraineComments(models.Model):
    """
    This is a mini project in order to find out toxic comments concerning Ukraine refugees
    """
    text = models.TextField()
    language = models.TextField(default=LANGUAGE.ENGLISH, choices=LANGUAGE.choices,
                                help_text="the language we are querying")
    conversation_id = models.BigIntegerField()
    toxicity_value = models.FloatField(null=True)
    platform = models.TextField(default=PLATFORM.TWITTER, choices=PLATFORM.choices, null=True,
                                help_text="the plattform used (twitter or reddit)")


class TWCandidateIntolerance(models.Model):
    """
    The idea is here to verify the "badness" of dictionary based terrible tweets and validate the categories
    """
    first_bad_word = models.TextField(null=True)
    tweet = models.OneToOneField(Tweet, on_delete=models.DO_NOTHING)
    dict_category = models.TextField(default=INTOLERANCE.NONE, choices=INTOLERANCE.choices, null=True,
                                     help_text="the category the bad word is grouped under in the dictionary")
    political_correct_word = models.TextField(null=True)


class TWIntoleranceRating(models.Model):
    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    candidate = models.ForeignKey(TWCandidateIntolerance, on_delete=models.DO_NOTHING)
    user_category = models.TextField(default=INTOLERANCE.NONE, choices=INTOLERANCE.choices, null=True,
                                     help_text="the category the intolerance could best be grouped by")
    u_intolerance_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                               help_text="Do you agree that the tweet is intolerant? (hateful or "
                                                         "insensitive towards a specific group)")
    u_sentiment_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the tweet expresses a positive sentiment?")
    u_clearness_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the meaning of the statement is clear from "
                                                       "the context?")
    u_person_hate = models.BooleanField(help_text="Is this comment directed against a person?")

    u_political_correct_word = models.CharField(null=True, blank=True, max_length=100,
                                                help_text="the correct label for the group")

    def get_absolute_url(self):
        return reverse('delab-label-intolerance-proxy')


class IntoleranceAnswer(models.Model):
    """
    This persist the answers based on the strategies and if it was sent to twitter the
    strategy chosen and the timestamp, when the answer was sent
    """
    candidate = models.OneToOneField(TWCandidateIntolerance, on_delete=models.DO_NOTHING)
    answer1 = models.CharField(max_length=250)
    answer2 = models.CharField(max_length=250)
    answer3 = models.CharField(max_length=250)
    strategy_chosen = models.TextField(default=STRATEGIES.NORMATIVE, choices=STRATEGIES.choices, null=True)
    date_success_sent = models.DateTimeField(blank=True, null=True)
    twitter_id = models.BigIntegerField(unique=True, null=True, blank=True)


class IntoleranceAnswerValidation(models.Model):
    """
    This is a utility table to hold the validation decisions of the users
    """
    answer = models.ForeignKey(IntoleranceAnswer, on_delete=models.DO_NOTHING)
    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    valid = models.BooleanField(help_text="Should this answer be sent to social media for the experiment?")
    comment = models.TextField(null=True, blank=True,
                               help_text="Plz write a comment why you don't think this is valid,"
                                         " if you think it is a bug!")

    def get_absolute_url(self):
        return reverse('delab-intolerance-answer-validation-proxy')


class FollowerNetwork(models.Model):
    source = models.ForeignKey(TweetAuthor, related_name="follower", on_delete=models.DO_NOTHING)
    target = models.ForeignKey(TweetAuthor, related_name="followed", on_delete=models.DO_NOTHING)
    relationship = models.TextField(default=NETWORKRELS.FOLLOWS, choices=NETWORKRELS.choices,
                                    help_text="the kind of relationship, could also be mentions or something else")

    class Meta:
        unique_together = ('source', 'target', 'relationship')


class ModerationCandidate2(models.Model):
    """
    represents the tweets which where selected using a dictionary approach.
    This table is also the selector for the manual labeling at the web-interface
    """
    tweet = models.OneToOneField(Tweet, on_delete=models.DO_NOTHING)
    exp_id = models.TextField(default="v0.0.1", help_text="This shows which version of the ditionary was used")
    c_sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    sentiment_value_norm = models.FloatField(null=True, help_text="the normalized sentiment measure ")
    c_author_number_changed_norm = models.FloatField(null=True,
                                                     help_text="the number of different authors posting before and after the tweet")
    c_author_topic_variance_norm = models.FloatField(null=True,
                                                     help_text="the normalized author diversity")
    moderator_index = models.FloatField(null=True,
                                        help_text="a combined measure of the quality of a tweet in terms of moderating value")

    u_moderator_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the tweet is moderating the conversation?")
    u_sentiment_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the tweet expresses a positive sentiment?")
    u_author_topic_variance_rating = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                                         help_text="Do you agree that the tweet has caused a greater variety of perspectives?")


class ModerationRating(models.Model):
    mod_coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    mod_candidate = models.ForeignKey(ModerationCandidate2, on_delete=models.DO_NOTHING)

    u_mod_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                       help_text="Do you agree that the tweet is moderating?")
    u_sis_issues = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                       help_text="Do you agree that the situation before the tweet was issue centered?")
    u_sit_consensus = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                          help_text="Do you agree that the situation before the tweet was consensus oriented?")
    u_mod_issues = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                       help_text="Do you agree that the moderating tweet tried to focus debating the issues (non-emotionally)?")
    u_mod_consensus = models.IntegerField(default=Likert.NOT_SURE, choices=Likert.choices, null=True,
                                          help_text="Do you agree that the moderating tweet tried to focus support consensus building?")
    u_clearness_rating = models.IntegerField(default=Likert.STRONGLY_NOT_AGREE, choices=Likert.choices, null=True,
                                             help_text="Do you agree that the meaning of the statement is clear from "
                                                       "the context?")
    u_moderating_part = models.TextField(null=True, blank=True,
                                         help_text="Please copy the part of the tweet that is moderating to here!")

    def get_absolute_url(self):
        return reverse('delab-label-moderation2-proxy')
