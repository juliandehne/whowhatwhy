import json
from twitter.util import TwitterConnector


def run():
    params = {'query': '(from:twitterdev -is:retweet) OR #twitterdev', 'tweet.fields': 'author_id', 'max_results': '12'}
    search_url = "https://api.twitter.com/2/tweets/search/all"

    connector = TwitterConnector()
    json_result = connector.get_from_twitter(search_url, params, True)
    print(json.dumps(json_result, indent=4, sort_keys=True))
