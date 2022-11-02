from delab.api.api_util import get_all_conversation_ids
from delab.corpus.download_conversations_proxy import download_conversations
from delab.corpus.download_conversations_twitter import download_conversation_as_tree, save_tree_to_db
from delab.delab_enums import PLATFORM
from delab.models import Tweet
from delab.network.conversation_network import get_nx_conversation_tree
from delab.tw_connection_util import DelabTwarc


def run():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        failed_tree = False
        try:
            get_nx_conversation_tree(conversation_id)
        except AssertionError as ae:
            failed_tree = True
        tweets = Tweet.objects.filter(conversation_id=conversation_id)
        count = tweets.count()
        if count < 5 or failed_tree:
            print(conversation_id)

            twarc = DelabTwarc()
            max_conversation_length = 50000
            root_node = download_conversation_as_tree(twarc, conversation_id, max_conversation_length)
            example_tweet: Tweet = Tweet.objects.filter(conversation_id=conversation_id).first()
            topic = example_tweet.topic.title
            simple_request = example_tweet.simple_request
            platform = example_tweet.platform
            if platform == PLATFORM.TWITTER:
                save_tree_to_db(root_node, topic, simple_request, conversation_id, platform)
            if PLATFORM == PLATFORM.REDDIT:
                download_conversations(topic=topic, simple_request=simple_request, language=example_tweet.language,
                                       platform=platform)
