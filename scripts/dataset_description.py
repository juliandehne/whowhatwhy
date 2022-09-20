from delab.delab_enums import PLATFORM
from delab.models import Tweet


def run():
    n_tweets = Tweet.objects.count()
    print("number of tweets is {}".format(n_tweets))
    n_tweets_reddit = Tweet.objects.filter(platform=PLATFORM.REDDIT).count()
    n_tweets_twitter = Tweet.objects.filter(platform=PLATFORM.TWITTER).count()
    print("n tweet reddit: {}, n tweet twitter: {}".format(n_tweets_reddit, n_tweets_twitter))
    n_conversations = len(set(Tweet.objects.values_list("conversation_id", flat=True).all()))
    print("n conversations: {}".format(n_conversations))
    n_conversations_reddit = len(
        set(Tweet.objects.filter(platform=PLATFORM.REDDIT).values_list("conversation_id", flat=True).all()))
    n_conversations_twitter = len(
        set(Tweet.objects.filter(platform=PLATFORM.TWITTER).values_list("conversation_id", flat=True).all()))
    print("n conversations reddit: {}, n conversations twitter: {}".format(n_conversations_reddit,
                                                                           n_conversations_twitter))
