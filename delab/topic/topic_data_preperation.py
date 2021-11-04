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
                t.tw_author = author
                t.save(update_fields=["tw_author"])
            except Exception:
                logger.error("author for tweet was not downloaded")
    else:
        logger.debug("no timeline was found for author {}".format(author_id))


def update_timelines_from_conversation_users(simple_request_id=-1):
    if simple_request_id < 0:
        author_ids = Tweet.objects.filter(
            ~Exists(Timeline.objects.filter(author_id=OuterRef("author_id")))).values_list(
            'author_id', flat=True).distinct()
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
