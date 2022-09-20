# Create your models here.
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse

from delab.delab_enums import VERSION, PLATFORM, LANGUAGE, Likert, INTOLERANCE, STRATEGIES, NETWORKRELS, \
    TWEET_RELATIONSHIPS, MODERATION
from delab.models import Tweet


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
    tweet = models.OneToOneField(Tweet, on_delete=models.CASCADE)
    dict_category = models.TextField(default=INTOLERANCE.NONE, choices=INTOLERANCE.choices, null=True,
                                     help_text="the category the bad word is grouped under in the dictionary")
    political_correct_word = models.TextField(null=True)


class TWIntoleranceRating(models.Model):
    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    candidate = models.ForeignKey(TWCandidateIntolerance, on_delete=models.CASCADE)
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
    candidate = models.OneToOneField(TWCandidateIntolerance, on_delete=models.CASCADE)
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
    answer = models.ForeignKey(IntoleranceAnswer, on_delete=models.CASCADE)
    coder = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    valid = models.BooleanField(help_text="Should this answer be sent to social media for the experiment?")
    comment = models.TextField(null=True, blank=True,
                               help_text="Plz write a comment why you don't think this is valid,"
                                         " if you think it is a bug!")

    def get_absolute_url(self):
        return reverse('delab-intolerance-answer-validation-proxy')
