import json

from django.db import IntegrityError

from delab.tw_connection_util import TwitterConnector

from twitter.models import Tweet, TwTopic
import requests


def run():
    # create topic
    topic_example = TwTopic()
    topic_example.title = "random"
    topic, created = TwTopic.objects.get_or_create(topic_example.__dict__)

    count = 500

    connector = TwitterConnector(1)

    random_stream_url = "https://api.twitter.com/2/tweets/sample/stream"

    headers = connector.create_headers()
    params = {'tweet.fields': 'lang'}
    response = requests.request("GET", random_stream_url, headers=headers, stream=True,
                                params=params)
    print("is connected {}".format(response.status_code))

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            while True:
                if count == 0:
                    break
                twitter_data: list = json_response.get("corpus")
                if twitter_data.get("lang") == "en":
                    print(json.dumps(json_response, indent=4, sort_keys=True))
                    count += -1
                    try:
                        tweet = Tweet()
                        tweet.topic = topic
                        tweet.query_string = topic_example.title
                        tweet.text = twitter_data.get("text")
                        tweet.twitter_id = twitter_data.get("id")
                        tweet.save()
                    except IntegrityError:
                        pass


