from delab.bot.moderation_bot import send_post
from delab.tw_connection_util import get_praw


def run():
    # reddit = get_praw()
    # print(reddit)
    intervention_id = 20
    send_post(intervention_id)
