import requests

from delab.tw_connection_util import send_tweet


def run():
    reply_to_id = 1392381001788235780
    url = "https://api.twitter.com/2/tweets"
    # payload = {}
    # reply = {"in_reply_to_tweet_id": reply_to_id, "quote_tweet_id": str(1444968676474728452)}
    # payload["text"] = "This is delabot! I like your work, keep it up!"
    # payload["reply"] = reply
    text = "Luckily we now have a postdoc but we still need student researchers! (this message was send automatically by delab app)"
    send_tweet(text, tweet_id=reply_to_id)
