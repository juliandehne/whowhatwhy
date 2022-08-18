import csv
import logging
from functools import partial

from delab.corpus.download_conversations_reddit import save_reddit_tree
from delab.corpus.download_conversations_util import set_up_topic_and_simple_request
from delab.models import Tweet, TweetSequence
from delab.tw_connection_util import get_praw
from scripts.download_corpus_john import topic
from util.abusing_strings import convert_to_hash

# create an artificial topic and query
simple_request, tw_topic = set_up_topic_and_simple_request("john reddit corpus 09_08_22", -1, topic)

logger = logging.getLogger(__name__)

debug = False


def run():
    with open('/home/dehne/ownCloud/delab/corpus/version1/reddit_tabelle.csv') as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        reddit = get_praw()

        submission_dict = {}
        readable_group_dict = {}
        for row in reader:
            reddit_url = row[0]
            reddit_url = reddit_url.replace("https://www.reddit.com/r/", "")
            reddit_url_fields = reddit_url.split("/")
            if len(reddit_url_fields) > 2:
                sub_reddit_string = reddit_url_fields[0]
                submission_id = reddit_url_fields[2]
            if len(reddit_url_fields) >= 4:
                post_id = reddit_url_fields[4]
                key = sub_reddit_string + "_" + row[1]
                submission_dict[key] = submission_id
                readable_group_dict_ids = readable_group_dict.get(key, [])
                readable_group_dict_ids.append(post_id)
                if submission_id not in readable_group_dict_ids:
                    readable_group_dict_ids.append(submission_id)
                readable_group_dict[key] = readable_group_dict_ids

        for key, value in readable_group_dict.items():
            if debug and len(value) > 10:
                continue
            sequence_name = str(key) + "_reddit_18_08_22"
            sequence_tweet_filter = partial(tweet_filter_reddit, value, sequence_name)
            submission_id_string = submission_dict[key]
            submission = reddit.submission(id=submission_id_string)
            save_reddit_tree(simple_request, submission, tw_topic, max_conversation_length=100000,
                             min_conversation_length=3, tweetfilter=sequence_tweet_filter)
            logger.debug("downloaded {} reddit posts:".format(
                TweetSequence.objects.filter(name=sequence_name).first().tweets.count()))
            if debug:
                break


def tweet_filter_reddit(sequence_ids, sequence_name, tweet):
    """
    this tweet_filter makes sure that the elements of the sequence are linked to the existing sequence
    :param sequence_ids:
    :param sequence_name:
    :param tweet:
    :return:
    """
    if Tweet.objects.filter(twitter_id=tweet.twitter_id).exists():
        tweet = Tweet.objects.filter(twitter_id=tweet.twitter_id).first()
    else:
        tweet.save()

    reddit_id = tweet.reddit_id
    if "_" in reddit_id:
        reddit_id = reddit_id.split("_")[1]
    if reddit_id in sequence_ids:
        if TweetSequence.objects.filter(name=sequence_name).exists():
            sequence = TweetSequence.objects.filter(name=sequence_name).get()
        else:
            sequence = TweetSequence.objects.create(name=sequence_name)
        sequence.tweets.add(tweet)
    return tweet
