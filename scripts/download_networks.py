from delab.models import Tweet
from delab.network import Neo4jDAO as dao
from delab.network.conversation_network import download_followers_recursively
from delab.tw_connection_util import DelabTwarc

twarc = DelabTwarc()


def run():
    conversation_id = 1463857436385759238
    user_ids = download_discussion_follower(conversation_id)
    download_followers_recursively(user_ids, 1)


