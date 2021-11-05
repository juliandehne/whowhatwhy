import json
import logging
import time

from django.db.models import Exists, OuterRef

from delab.models import Timeline, Tweet, TweetAuthor
from delab.magic_http_strings import TWEETS_USER_URL
from delab.tw_connection_util import DelabTwarc

logger = logging.getLogger(__name__)


def save_author_tweet_to_tb(json_result, author_id):
    if "data" in json_result:
        data = json_result["data"]
        for tweet_dict in data:
            in_reply_to_user_id = tweet_dict.get("in_reply_to_user_id", None)

            t, created = Timeline.objects.get_or_create(
                text=tweet_dict["text"],
                created_at=tweet_dict["created_at"],
                author_id=author_id,
                tweet_id=tweet_dict["id"],
                conversation_id=tweet_dict["conversation_id"],
                in_reply_to_user_id=in_reply_to_user_id,
                lang=tweet_dict["lang"]
            )
            t.full_clean()
            try:
                author = TweetAuthor.objects.filter(twitter_id=t.author_id).get()
                author.has_timeline = True
                author.save(update_fields=["has_timeline"])
                t.tw_author = author
                t.save(update_fields=["tw_author"])
            except Exception:
                logger.error("author for tweet was not downloaded")
    else:
        logger.debug("no timeline was found for author {}".format(author_id))


def fix_legacy():
    # update authors "has_timeline" field
    authors = TweetAuthor.objects.filter(has_timeline__isnull=True)
    authors_ids = authors.values_list('twitter_id', flat=True)
    existing_timelines = Timeline.objects.filter(author_id__in=authors_ids).select_related("tw_author")
    for existing_timeline in existing_timelines:
        try:
            author = existing_timeline.tw_author
            if author is None:
                author = TweetAuthor.objects.filter(twitter_id=existing_timeline.author_id).get()
                # author = authors.filter(twitter_id=existing_timeline.author_id).get()
            author.has_timeline = True
            author.save(update_fields=["has_timeline"])
            existing_timeline.tw_author = author
            existing_timeline.save(update_fields=["tw_author"])
        except Exception:
            logger.error("not all authors have been downloaded prior to timeline downloads")
    # update timelines that did not store the associated author object
    existing_timelines2 = Timeline.objects.filter(tw_author__isnull=True).all()
    for existing_timeline2 in existing_timelines2:
        try:
            author = TweetAuthor.objects.get(twitter_id=existing_timeline2.author_id)
            existing_timeline2.tw_author = author
            existing_timeline2.save(update_fields=["tw_author"])
        except TweetAuthor.DoesNotExist:
            logger.error("author was not downloaded before updating timelines")


def update_timelines_from_conversation_users(simple_request_id=-1, fix_legacy_db=True):
    if simple_request_id < 0:
        author_ids = TweetAuthor.objects.filter(has_timeline__isnull=True).values_list('twitter_id', flat=True)
        if fix_legacy_db:
            fix_legacy()
    else:
        author_ids = Tweet.objects.filter(~Exists(Timeline.objects.filter(author_id=OuterRef("author_id")))).filter(
            simple_request_id=simple_request_id).values_list('author_id', flat=True).distinct()
    get_user_timeline_twarc(author_ids)


def get_user_timeline_twarc(author_ids, max_results=10):
    twarc_connector = DelabTwarc()

    author_count = 0
    for author_id in author_ids:
        author_count += 1
        logger.debug("computed {}/{} of the timelines".format(author_count, len(author_ids)))
        count = 0
        tweets = twarc_connector.timeline(user=author_id, max_results=min(max_results, 64), exclude_retweets=True,
                                          exclude_replies=True)
        for tweet in tweets:
            count += 1
            if count > max_results:
                break
            save_author_tweet_to_tb(tweet, author_id)
        if count == 0:
            logger.debug("could not find a timeline for the give")
            author = TweetAuthor.objects.filter(twitter_id=author_id).get()
            author.has_timeline = False
            author.save(update_fields=["has_timeline"])
