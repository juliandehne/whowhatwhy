from delab.tw_connection_util import DelabTwarc


def run():
    example_post = "https://twitter.com/Bibiana610/status/1496339405258342402"

    twarc = DelabTwarc()

    tweets = twarc.tweet_lookup([1496339405258342402])
    for tweet in tweets:
        print(tweet)
