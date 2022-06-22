from delab.models import Tweet

from delab.network.conversation_network import download_followers_recursively, download_discussion_follower
from delab.tw_connection_util import DelabTwarc

twarc = DelabTwarc()


def run():
    conversation_ids = set(Tweet.objects.values_list('conversation_id', flat=True))
    if len(conversation_ids) > 10:
        for conversation_id in list(conversation_ids)[:10]:
            user_ids = download_discussion_follower(conversation_id)
            download_followers_recursively(user_ids, 3)
    else:
        for conversation_id in conversation_ids:
            user_ids = download_discussion_follower(conversation_id)
            download_followers_recursively(user_ids, 3)
