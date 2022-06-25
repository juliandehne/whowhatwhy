import logging

from django.db.models import Exists, OuterRef

from delab.models import Tweet, TweetAuthor, FollowerNetwork
from delab.network.conversation_network import download_followers_recursively, get_participants
from delab.tw_connection_util import DelabTwarc

twarc = DelabTwarc()

logger = logging.getLogger(__name__)


def run():
    levels = 1
    n_conversations = 2
    count = 0
    conversation_ids = set(Tweet.objects.values_list('conversation_id', flat=True))
    unhandled_conversation_ids = prevent_multiple_downloads(conversation_ids)
    conversation_ids = unhandled_conversation_ids
    if len(conversation_ids) > 10 and n_conversations > 0:
        conversation_ids = list(conversation_ids)[:n_conversations]
        for conversation_id in conversation_ids:
            count += 1
            user_ids = get_participants(conversation_id)
            download_followers_recursively(user_ids, levels, following=True)
            logger.debug(" {}/{} conversations finished".format(count, len(conversation_ids)))
    else:
        for conversation_id in conversation_ids:
            count += 1
            user_ids = get_participants(conversation_id)
            download_followers_recursively(user_ids, levels, following=True)
            logger.debug(" {}/{} conversations finished".format(count, len(conversation_ids)))


def prevent_multiple_downloads(conversation_ids):
    unhandled_conversation_ids = []
    for conversation_id in conversation_ids:
        authors_is = set(Tweet.objects.filter(conversation_id=conversation_id).values_list("author_id", flat=True))
        author_part_of_networks = TweetAuthor.objects.filter(twitter_id__in=authors_is). \
            filter(Exists(FollowerNetwork.objects.filter(source_id=OuterRef('pk')))
                   | Exists(FollowerNetwork.objects.filter(target_id=OuterRef('pk')))).distinct()
        assert len(authors_is) > 0
        if not len(author_part_of_networks) > len(authors_is) / 2:
            unhandled_conversation_ids.append(conversation_id)
        else:
            logger.debug("conversation {} has been handled before".format(conversation_id))
    return unhandled_conversation_ids
