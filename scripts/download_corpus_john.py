from functools import partial

from delab.corpus.download_conversations_twitter import download_conversation_as_tree, save_tree_to_db
from delab.corpus.download_conversations_util import set_up_topic_and_simple_request
from delab.delab_enums import PLATFORM
from delab.models import TweetSequence, Tweet
from delab.tw_connection_util import DelabTwarc

topic = "culturalscripts"


def run():
    f = open('/home/dehne/ownCloud/delab/corpus/version1/twitter_urls.txt', 'r')

    content = f.read()
    content = content.replace("\n", "")
    content = content + "  504"
    groups = content.split(". ")[1:]

    group_dict = {}
    for group in groups:
        group_id = group[-3:]
        if group_id in group_dict:
            print("wtf")
        group = group[:-3]
        group = group.strip()
        group_members = group.split(",")
        group_dict[group_id] = group_members

    twarc = DelabTwarc()
    for key, value in group_dict.items():
        candidate_id = value[0].split("/")[-1]
        tweet = next(twarc.tweet_lookup([candidate_id]))
        if "data" in tweet:
            tweet = tweet["data"][0]
            sequence_ids = []
            for post in value:
                sequence_id = post.split("/")[-1]
                sequence_ids.append(sequence_id)
            conversation_id = tweet["conversation_id"]
            downloaded_tree = download_conversation_as_tree(twarc, conversation_id, 100000)

            sequence_tweet_filter = partial(tweet_filter, sequence_ids, str(key) + "_twitter_09_08_22")

            simple_request, twtopic = set_up_topic_and_simple_request("john twitter corpus 09_08_22", -1, topic)
            save_tree_to_db(downloaded_tree, twtopic, simple_request, conversation_id, PLATFORM.TWITTER,
                            tweet_filter=sequence_tweet_filter)
        else:
            print(tweet)


def tweet_filter(sequence_ids, sequence_name, tweet):
    if Tweet.objects.filter(twitter_id=tweet.twitter_id).exists():
        tweet = Tweet.objects.filter(twitter_id=tweet.twitter_id).first()
    else:
        tweet.save()

    if tweet.twitter_id in sequence_ids:
        if TweetSequence.objects.filter(name=sequence_name).exists():
            sequence = TweetSequence.objects.filter(name=sequence_name).get()
        else:
            sequence = TweetSequence.objects.create(name=sequence_name)
        sequence.tweets.add(tweet)
    return tweet
