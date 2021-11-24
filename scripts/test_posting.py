import requests

from delab.tw_connection_util import send_tweet


def run():
    reply_to_id = 1448614414962372619
    url = "https://api.twitter.com/2/tweets"
    # payload = {}
    # reply = {"in_reply_to_tweet_id": reply_to_id, "quote_tweet_id": str(1444968676474728452)}
    # payload["text"] = "This is delabot! I like your work, keep it up!"
    # payload["reply"] = reply
    text = "This is delabot! Your post is a little one-sided! Of course, not all scientific results, for example Covid modelling!"
    send_tweet(text, tweet_id=reply_to_id)
