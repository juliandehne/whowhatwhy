from requests_oauthlib import OAuth1Session
import os
import json
import yaml
import io


filename="C:\\Users\\julia\\PycharmProjects\\djangoProject\\twitter\\secret\\keys_simple.yaml"

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")

access_token = ""
access_token_secret = ""

with open(filename) as f:
    my_dict = yaml.safe_load(f)
    if consumer_key != "":
        consumer_key = my_dict.get("consumer_key")
    if consumer_secret != "":
        consumer_secret = my_dict.get("consumer_secret")
    access_token = my_dict.get("access_token")
    access_token_secret = my_dict.get("access_token_secret")

# You can adjust ids to include a single Tweets
# Or you can add to up to 100 comma-separated IDs
params = {"ids": "1278747501642657792", "tweet.fields": "created_at"}

# Tweet fields are adjustable.
# Options include:
# attachments, author_id, context_annotations,
# conversation_id, created_at, entities, geo, id,
# in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
# possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
# source, text, and withheld

#request_token_url = "https://api.twitter.com/oauth/request_token"
#oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    response = oauth.get(
        "https://api.twitter.com/2/tweets", params=params
    )

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))

except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )
