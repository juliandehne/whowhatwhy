from delab.api.api_util import get_all_conversation_ids
from delab.models import Tweet
from delab.network.conversation_network import get_nx_conversation_tree


def run():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        failed_tree = False
        try:
            get_nx_conversation_tree(conversation_id)
        except AssertionError as ae:
            print(ae)
            failed_tree = True
        tweets = Tweet.objects.filter(conversation_id=conversation_id)
        count = tweets.count()
        if count < 5 or failed_tree:
            print(conversation_id)
            for tweet in tweets:
                tweet.delete()
