import json
import logging
import time

from django.db.models import Exists, OuterRef

from delab.models import Timeline, Tweet
from delab.magic_http_strings import TWEETS_USER_URL
from delab.tw_connection_util import TwitterConnector

logger = logging.getLogger(__name__)


def save_author_tweet_to_tb(json_result, author_id):
    if "corpus" in json_result:
        data = json_result["corpus"]
        for tweet_dict in data:
            if "in_reply_to_user_id" in tweet_dict:
                in_reply_to_user_id = tweet_dict["in_reply_to_user_id"]
            else:
                in_reply_to_user_id = None
            t, created = Timeline.objects.get_or_create(
                text=tweet_dict["text"],
                created_at=tweet_dict["created_at"],
                author_id=author_id,
                tweet_id=tweet_dict["id"],
                conversation_id=tweet_dict["conversation_id"],
                in_reply_to_user_id=in_reply_to_user_id,
                lang=tweet_dict["lang"]
            )


def get_user_timeline(author_id, connector, params={},
                      iterations=1):
    if iterations > 0:
        json_result = connector.get_from_twitter(TWEETS_USER_URL.format(author_id), params)
        logger.debug(json.dumps(json_result, indent=4, sort_keys=True))
        save_author_tweet_to_tb(json_result, author_id)
        if "meta" in json_result:
            if "next_token" not in json_result["meta"]:
                print("reached end of results for user with id{}".format(author_id))
            else:
                params["pagination_token"] = (json_result["meta"])["next_token"]
                time.sleep(2)  # twitter api expects this timeout
                get_user_timeline(author_id, connector, params, iterations - 1)
        else:
            print("reached end of results for user with id{}".format(author_id))
    else:
        print("[jd] reached max iterations")


def update_timelines_from_conversation_users():
    tweets = Tweet.objects.filter(~Exists(Timeline.objects.filter(author_id=OuterRef("author_id")))).all()
    logger.info(len(tweets))

    connector = TwitterConnector()
    params = {"max_results": 100,
              "tweet.fields": "in_reply_to_user_id,created_at,conversation_id,lang,text"}
    for tweet in tweets:
        get_user_timeline(tweet.author_id, connector, params=params, iterations=5)
