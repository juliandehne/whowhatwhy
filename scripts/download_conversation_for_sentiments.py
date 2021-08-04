from delab.download_conversations import *
from twitter.tw_connection_util import TwitterStreamConnector


def run():
    # download_conversations("Inferno", ["Feuer", "Licht"])
    connector = TwitterStreamConnector()

    sample_rules = [
        {"value": "dog has:images", "tag": "dog pictures"},
        {"value": "cat has:images -grumpy", "tag": "cat pictures"},
    ]
    connector.set_rules(sample_rules)
    query = {"tweet.fields": "created_at", "expansions": "author_id", "user.fields": "created_at"}
    connector.get_stream(query, pretty_print_stream)


def pretty_print_stream(json_response):
    print(json.dumps(json_response, indent=4, sort_keys=True))
    return False
