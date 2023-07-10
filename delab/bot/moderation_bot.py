import logging

from delab.delab_enums import PLATFORM
from delab.models import Tweet
from delab.tw_connection_util import get_praw
from mt_study.models import Intervention

logger = logging.getLogger(__name__)


def send_post(intervention_id, platform=PLATFORM.REDDIT):
    logger.debug("send out moderation post {}".format(intervention_id))
    # TODO implement
    last_post = get_last_post(intervention_id)
    if platform == PLATFORM.REDDIT:
        send_rd_post(intervention_id, last_post)


def send_rd_post(intervention_id, last_post: Tweet):
    reddit = get_praw()

    submission_url = last_post.original_url
    intervention = Intervention.objects.filter(id=intervention_id).get()
    comment_text = intervention.text
    submission = reddit.submission(url=submission_url)
    submission.reply(comment_text)
    intervention.sent = True
    intervention.save(update_fields=['sent'])


def get_last_post(intervention_id):
    intervention = Intervention.objects.filter(id=intervention_id).get()
    tweets = list(intervention.flow.tweets.all())
    tweets.sort(key=lambda x: x.created_at, reverse=True)
    last_tweet = tweets[0]
    return last_tweet
