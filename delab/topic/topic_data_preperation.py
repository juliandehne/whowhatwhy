import json
import logging
import time

from django.db.models import Exists, OuterRef

from delab.models import Timeline, Tweet
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


def get_user_timeline(author_id, connector, params={},
                      iterations=1):
    if iterations > 0:
        json_result = connector.get_from_twitter(TWEETS_USER_URL.format(author_id), params)
        # logger.debug(json.dumps(json_result, indent=4, sort_keys=True))
        save_author_tweet_to_tb(json_result, author_id)
        if "meta" in json_result:
            if "next_token" not in json_result["meta"] or json_result["meta"]["result_count"] == 0:
                logger.debug("reached end of results for user with id{}".format(author_id))
            else:
                params["pagination_token"] = (json_result["meta"])["next_token"]
                time.sleep(2)  # twitter api expects this timeout
                get_user_timeline(author_id, connector, params, iterations - 1)
        else:
            logger.debug("reached end of results for user with id{}".format(author_id))
    else:
        logger.debug("[jd] reached max iterations")


def update_timelines_from_conversation_users(simple_request_id=-1):
    if simple_request_id < 0:
        author_ids = Tweet.objects.filter(
            ~Exists(Timeline.objects.filter(author_id=OuterRef("author_id")))).values_list(
            'author_id', flat=True)
    else:
        author_ids = Tweet.objects.filter(~Exists(Timeline.objects.filter(author_id=OuterRef("author_id")))).filter(
            simple_request_id=simple_request_id).values_list('author_id', flat=True)
    get_user_timeline_twarc(author_ids)


def get_user_timeline_twarc(author_ids):
    twarc_connector = DelabTwarc()

    for author_id in author_ids:
        tweets = twarc_connector.timeline(user=author_id)
        for tweet in tweets:
            save_author_tweet_to_tb(tweet, author_id)
