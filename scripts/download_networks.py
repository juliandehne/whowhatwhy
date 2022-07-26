import logging

from delab.network.conversation_network import download_twitter_follower
from delab.tw_connection_util import DelabTwarc

twarc = DelabTwarc()

logger = logging.getLogger(__name__)


def run():
    levels = 1
    n_conversations = -1
    download_twitter_follower(levels, n_conversations)
