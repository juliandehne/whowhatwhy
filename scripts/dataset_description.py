from delab.delab_enums import PLATFORM
from delab.models import Tweet, TweetSequence


def run():
    topic_id = 12  # cultural scripts
    tweets = Tweet.objects.filter(topic_id=topic_id)
    n_tweets = tweets.count()
    print("number of tweets is {}".format(n_tweets))
    reddit_tweets = Tweet.objects.filter(platform=PLATFORM.REDDIT, topic_id=topic_id)
    n_tweets_reddit = reddit_tweets.count()
    twitter_tweets = Tweet.objects.filter(platform=PLATFORM.TWITTER, topic_id=topic_id)
    n_tweets_twitter = twitter_tweets.count()
    print("n tweet reddit: {}, n tweet twitter: {}".format(n_tweets_reddit, n_tweets_twitter))
    n_conversations = len(set(Tweet.objects.filter(topic_id=topic_id).values_list("conversation_id", flat=True).all()))
    print("n conversations: {}".format(n_conversations))
    n_conversations_reddit = len(
        set(Tweet.objects.filter(platform=PLATFORM.REDDIT, topic_id=topic_id).values_list("conversation_id",
                                                                                          flat=True).all()))
    n_conversations_twitter = len(
        set(Tweet.objects.filter(platform=PLATFORM.TWITTER, topic_id=topic_id).values_list("conversation_id",
                                                                                           flat=True).all()))
    print("n conversations reddit: {}, n conversations twitter: {}".format(n_conversations_reddit,
                                                                           n_conversations_twitter))

    n_sequences = len(set(TweetSequence.objects.filter(tweets__in=tweets).values_list("name", flat=True)))
    n_sequences_reddit = len(set(TweetSequence.objects.filter(tweets__in=reddit_tweets).values_list("name", flat=True)))
    n_sequences_twitter = len(set(TweetSequence.objects.filter(tweets__in=twitter_tweets).values_list("name", flat=True)))
    print("n sequences reddit: {}, n sequences twitter = {}".format(n_sequences_reddit, n_sequences_twitter))
