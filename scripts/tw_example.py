import json
from twitter.util import TwitterConnector

# You can adjust ids to include a single Tweets
# Or you can add to up to 100 comma-separated IDs
# params = {"ids": "1278747501642657792", "tweet.fields": "created_at"}
# search_url = "https://api.twitter.com/2/tweets"

params = {'query': '(from:twitterdev -is:retweet) OR #twitterdev', 'tweet.fields': 'author_id', 'max_results': '12'}
search_url = "https://api.twitter.com/2/tweets/search/all"

connector = TwitterConnector(1)
json_result = connector.get_from_twitter(search_url, params, True)
print(json.dumps(json_result, indent=4, sort_keys=True))
