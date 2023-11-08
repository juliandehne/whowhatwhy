import logging

from delab.delab_enums import PLATFORM
from delab.models import Tweet
from delab.tw_connection_util import get_praw
from mt_study.models import Intervention
from delab.tw_connection_util import create_mastodon
from mastodon import Mastodon

logger = logging.getLogger(__name__)


def send_post(intervention_id):
    logger.debug("send out moderation post {}".format(intervention_id))
    # TODO implement
    last_post, is_submission = get_parent_post(intervention_id)
    platform = last_post.platform
    if platform == PLATFORM.REDDIT:
        send_rd_post(intervention_id, last_post, is_submission)
    if platform == PLATFORM.MASTODON:
        send_mstd_post(intervention_id, last_post)


def send_rd_post(intervention_id, last_post: Tweet, is_submission):

    reddit = get_praw()

    submission_url = last_post.original_url
    intervention = Intervention.objects.filter(id=intervention_id).get()
    if intervention.sent is not True:
        comment_text = intervention.text
        if is_submission:
            original_comment = reddit.submission(url=submission_url)
        else:
            original_comment = reddit.comment(url=submission_url)
        original_comment.reply(comment_text)
        intervention.sent = True
        intervention.save(update_fields=['sent'])


def send_mstd_post(intervention_id, last_post):
    parent_id = last_post.twitter_id
    mastodon = create_mastodon()
    intervention = Intervention.objects.filter(id=intervention_id).get()
    if intervention.sent is not True:
        comment_text = intervention.text
        mastodon.status_post(status=comment_text, in_reply_to_id=parent_id)
        intervention.sent = True
        intervention.save(update_fields=['sent'])


def get_parent_post(intervention_id):
    intervention = Intervention.objects.filter(id=intervention_id).get()
    position = intervention.position_in_flow
    if position > 0:
        position = position - 1
    tweets = list(intervention.flow.tweets.all())
    tweets.sort(key=lambda x: x.created_at)
    last_tweet = tweets[position]
    return last_tweet, position == 0

