from delab.corpus.filter_sequences import get_path
from delab.models import Tweet


def compute_context(candidate, context):
    """
    this computes the context in which the statement (tweet, reddict comment) was dropped.
     It takes the two parents from the reply tree and the next two children assuming that a path of length 3 <= n <=5
     exists
    :param candidate:
    :param context:
    :return:
    """

    tweet_text = candidate.tweet.text
    tweet_id = candidate.tweet.id
    twitter_id = candidate.tweet.twitter_id
    conversation_id = candidate.tweet.conversation_id
    # context["text"] = clean_corpus([tweet_text])[0]
    context["text"] = tweet_text
    context["tweet_id"] = tweet_id
    path = get_path(twitter_id, conversation_id)

    root_tweet = Tweet.objects.filter(conversation_id=conversation_id, tn_parent__isnull=True).first().text
    context["root_tweet"] = root_tweet
    if path is not None:
        context_tweets = Tweet.objects.filter(twitter_id__in=path) \
            .order_by('created_at')
        full_conversation = list(context_tweets.values_list("text", flat=True))
        # index = full_conversation.index(tweet_text)
        # full_conversation = clean_corpus(full_conversation)
        context["conversation"] = full_conversation
    else:
        context["conversation"] = [tweet_text]
        """
        context_tweets = Tweet.objects.filter(conversation_id=candidate.tweet.conversation_id) \
            .order_by('created_at')
        full_conversation = list(context_tweets.values_list("text", flat=True))
        index = full_conversation.index(tweet_text)

        # full_conversation = clean_corpus(full_conversation)
        context["conversation"] = full_conversation[index - 2:index + 3]

        context["conversation"]
        """
    return context
