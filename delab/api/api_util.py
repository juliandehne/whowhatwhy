from django.utils.encoding import smart_text
from django_pandas.io import read_frame
from rest_framework import renderers

from delab.delab_enums import PLATFORM
from delab.models import Tweet


def get_standard_field_names():
    return ["twitter_id",
            "conversation_id",
            "author_id",
            "created_at",
            "in_reply_to_user_id",
            "text", "tw_author__name", "tw_author__location", "topic__title"]


class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class TabbedTextRenderer(renderers.BaseRenderer):
    # here starts the wonky stuff
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return smart_text(data, encoding=self.charset)


def get_file_name(conversation_id, full, suffix):
    return str(conversation_id) + "_conversation_" + full + suffix


def get_all_conversation_ids(topic=None):
    if topic is not None:
        result = Tweet.objects.filter(topic__title=topic, language__in=["en", "de"]).distinct(
            "conversation_id").values_list("conversation_id",
                                           flat=True).all()
    else:
        result = Tweet.objects.filter(language__in=["en", "de"]).distinct("conversation_id").values_list(
            "conversation_id",
            flat=True).all()
    result = list(result)
    return result


def get_all_twitter_conversation_ids():
    result = Tweet.objects.filter(language__in=["en", "de"], platform=PLATFORM.TWITTER).distinct(
        "conversation_id").values_list(
        "conversation_id",
        flat=True).all()
    return result


def get_author_tweet_map(conversation_id):
    """

    @param conversation_id:
    @return: tweet2author and author2tweetsmaps with the author being the author_id in the tweet table aka.
    the twitter id for an author not the id of the tweetauthor table
    """
    tweets = Tweet.objects.filter(conversation_id=conversation_id).only("author_id", "twitter_id")
    tweet2author = {}
    author2tweets = {}
    for tweet in tweets:
        tweet2author[tweet.twitter_id] = tweet.author_id
        if tweet.author_id in author2tweets:
            author_tweets = author2tweets.get(tweet.author_id)
            author_tweets.append(tweet.twitter_id)
        else:
            author2tweets[tweet.author_id] = [tweet.twitter_id]
    return tweet2author, author2tweets


def get_conversation_dataframe(topic_string: str, conversation_id: int = None):
    if conversation_id is not None:
        qs = Tweet.objects.filter(conversation_id=conversation_id, topic__title=topic_string).all()
    else:
        qs = Tweet.objects.filter(topic__title=topic_string).all()
    df = add_parents_to_frame(qs)
    return df


def add_parents_to_frame(qs):
    """
    There seems to be bug in the django-pandas api that self-foreign keys are not returned properly
    This is a workaround
    :param qs:
    :return:
    """
    tn_parent_ids = qs.values_list("tn_parent_id", flat=True).all()
    df = read_frame(qs.all(), fieldnames=get_standard_field_names(), verbose=True)
    df['tn_parent_id'] = tn_parent_ids
    df['tn_parent_id'] = df['tn_parent_id'].astype('Int64')
    df['in_reply_to_user_id'] = df['in_reply_to_user_id'].astype('Int64')
    return df
