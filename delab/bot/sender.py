import logging

from delab.models import Tweet
from delab.tw_connection_util import send_tweet

logger = logging.getLogger(__name__)


def publish_moderation(instance):
    text = instance.text
    parent_tweet = Tweet.objects.filter(id=instance.tn_parent).get()
    reply_to_id = parent_tweet.twitter_id
    response = send_tweet(text, tweet_id=reply_to_id)
    logger.info(response)
    logger.info("send tweet {}".format(instance))
