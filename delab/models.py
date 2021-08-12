from django.db import models

# Create your models here.
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse

from django.core.management import call_command
import twitter


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
