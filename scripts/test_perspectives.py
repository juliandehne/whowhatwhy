import json
import time

from delab.models import PLATFORM
from delab.toxicity.perspectives import get_client, UkraineComment
from delab.tw_connection_util import DelabTwarc
from delab.models import UkraineComments
import re


def run():
    twarc = DelabTwarc()
    recent_tweets = twarc.search_recent(query="Ukraine Flüchtlinge", )

    comments = []
    counter = 0
    # each loop downloads 100 by default I think
    while counter < 100:
        tweet_dict = next(recent_tweets)
        for recent_tweet in tweet_dict["data"]:
            comment = UkraineComment(recent_tweet["text"], recent_tweet["lang"],
                                     recent_tweet["conversation_id"],
                                     PLATFORM.TWITTER)
            if comment.language == "de" or comment.language == "en":
                comments.append(comment)
        counter += 1

    client = get_client()

    for comment in comments:
        if len(comment.text) > 1:
            try:
                analyze_request = {
                    'comment': {
                        'text': comment.text},
                    'requestedAttributes': {'SEVERE_TOXICITY': {}}
                }
                response = client.comments().analyze(body=analyze_request).execute()
                comment.set_toxicity(response["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"])
                time.sleep(2)
            except Exception:
                print("something went wrong")

    for comment in comments:
        # if comment.toxicity_value > 0.5:
        UkraineComments.objects.create(
            **comment.__dict__
        )


def clean_text(text):
    temp = text
    # removing hashtags
    # temp = re.sub("@[A-Za-z0-9_]+", "", temp)
    # temp = re.sub("#[A-Za-z0-9_]+", "", temp)
    # removing links
    temp = re.sub(r"http\S+", "", temp)
    temp = re.sub(r"www.\S+", "", temp)
    # removing punctuation
    # temp = re.sub('[()!?]', ' ', temp)
    # temp = re.sub("\[.*?\]", ' ', temp)
    # alphanumeric
    temp = re.sub("[^a-z0-9A-ZäöüÄÖÜ\\.\\?\\!]", " ", temp)
    temp = re.sub("RT", "", temp)
    temp = temp.strip()
    return temp
