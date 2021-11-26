import datetime
import logging

import prawcore
from django.db import IntegrityError

from delab.tw_connection_util import get_praw
from delab.models import TweetAuthor, Tweet, PLATFORM, SimpleRequest, TwTopic
from util.abusing_strings import convert_to_hash

"""
get the moderators like this
https://praw.readthedocs.io/en/stable/code_overview/other/subredditmoderation.html

for message in reddit.subreddit("mod").mod.inbox(limit=5):
    print(f"From: {message.author}, Body: {message.body}")
    for reply in message.replies:
        print(f"From: {reply.author}, Body: {reply.body}")

"""

logger = logging.getLogger(__name__)


def download_conversations_reddit(topic_string, simple_request_id):
    # create the topic and save it to the db
    simple_request, topic = get_simple_request(simple_request_id, topic_string)
    reddit = get_praw()

    for submission in reddit.subreddit(topic_string).hot(limit=10):
        submission.comments.replace_more(limit=None)
        comments = submission.comments.list()
        if len(comments) >= 10:
            created = save_reddit_submission(submission, simple_request, topic)
            if created:
                for comment in comments:
                    save_reddit_entry(comment, simple_request, topic)


def save_reddit_submission(comment, simple_request, topic):
    author_id = compute_author_id(comment)
    created_time = datetime.datetime.fromtimestamp(comment.created)
    banned_at = None
    # create the author
    author, created = TweetAuthor.objects.get_or_create(
        twitter_id=author_id,
        name=comment.author.name,
        screen_name=comment.author.fullname,
        platform=PLATFORM.REDDIT
    )
    tweet_id = convert_to_hash(comment.selftext)
    conversation_id = convert_to_hash(comment.id)
    text = comment.title + "\n" + comment.selftext

    language = comment.subreddit.lang
    try:
        tweet, tweet_created = Tweet.objects.get_or_create(
            twitter_id=tweet_id,
            text=text,
            author_id=author_id,
            language=language,
            platform=PLATFORM.REDDIT,
            created_at=created_time,
            conversation_id=conversation_id,
            simple_request=simple_request,
            topic=topic,
            tw_author=author,
            banned_at=banned_at
        )
        return tweet_created
    except IntegrityError:
        return True


def compute_author_id(comment):
    author_id = convert_to_hash(comment.author.id)
    return author_id


def save_reddit_entry(comment, simple_request, topic):
    try:
        if comment.author:

            if hasattr(comment.author, 'id'):
                author_id = convert_to_hash(comment.author.id)
            else:
                author_id = convert_to_hash(comment.author.name)

            created_time = datetime.datetime.fromtimestamp(comment.created)
            # create the author
            fullname = ""
            if hasattr(comment.author, "fullname"):
                fullname = comment.author.fullname
            author, created = TweetAuthor.objects.get_or_create(
                twitter_id=author_id,
                name=comment.author.name,
                screen_name=fullname,
                platform=PLATFORM.REDDIT
            )

            tweet_id = convert_to_hash(comment.id)
            banned_at = None
            if comment.banned_at_utc:
                banned_at = datetime.datetime.fromtimestamp(comment.banned_at_utc)

            conversation_id = convert_to_hash(comment.submission.id)

            parent_id = comment.parent_id.split("_")[1]
            tn_parent = convert_to_hash(parent_id)
            if tn_parent == conversation_id:
                # if the comments are in the second hierarchy level the id should be the generated root id for that conversation
                try:
                    tn_parent = Tweet.objects.filter(conversation_id=conversation_id,
                                                     tn_parent__isnull=True).get().twitter_id
                except Exception:
                    logger.error("could not find parent in second hierarchy TODO DEBUG")
            # create the tweet
            text = comment.body
            language = comment.submission.subreddit.lang
            try:
                tweet, tweet_created = Tweet.objects.get_or_create(
                    twitter_id=tweet_id,
                    text=text,
                    author_id=author_id,
                    tn_parent_id=tn_parent,
                    language=language,
                    platform=PLATFORM.REDDIT,
                    created_at=created_time,
                    conversation_id=conversation_id,
                    simple_request=simple_request,
                    topic=topic,
                    tw_author=author,
                    banned_at=banned_at
                )
            except IntegrityError:
                return True
            return tweet_created
    except prawcore.exceptions.NotFound:
        logger.error("could not find something on reddit anymore")


def get_simple_request(simple_request_id, topic_string):
    topic, created = TwTopic.objects.get_or_create(
        title=topic_string
    )
    # save the request to the db in order to link the results in the view to the hashtags entered
    if simple_request_id > 0:
        simple_request, created = SimpleRequest.objects.get_or_create(
            pk=simple_request_id,
            topic=topic
        )
    else:
        request_string = "reddit top x submissions"
        simple_request, created = SimpleRequest.objects.get_or_create(
            title=request_string
        )
    return simple_request, topic
