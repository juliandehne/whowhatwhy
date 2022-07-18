import logging

from django.db.models import Exists, OuterRef

from delab.models import Tweet, TweetAuthor, FollowerNetwork
from delab.network.conversation_network import download_followers_recursively, get_participants, \
    prevent_multiple_downloads, restrict_conversations_to_reasonable, download_conversation_network
from delab.tw_connection_util import DelabTwarc

twarc = DelabTwarc()

logger = logging.getLogger(__name__)


def run():
    levels = 3
    n_conversations = -1
    count = 0
    conversation_ids = set(Tweet.objects.values_list('conversation_id', flat=True))
    conversation_ids = prevent_multiple_downloads(conversation_ids)
    conversation_ids = restrict_conversations_to_reasonable(conversation_ids)
    if len(conversation_ids) > n_conversations > 0:
        conversation_ids = list(conversation_ids)[:n_conversations]
        for conversation_id in conversation_ids:
            count += 1
            download_conversation_network(conversation_id, conversation_ids, count, levels)
    else:
        if len(conversation_ids) < n_conversations > 0:
            for conversation_id in conversation_ids:
                count += 1
                download_conversation_network(conversation_id, conversation_ids, count, levels)
        else:
            for conversation_id in conversation_ids:
                count += 1
                download_conversation_network(conversation_id, conversation_ids, count, levels)
    logger.info("finished downloading networks")

