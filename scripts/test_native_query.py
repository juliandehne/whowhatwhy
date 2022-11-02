"""
trying to improve this access

  tweets = Tweet.objects.filter(tn_parent__isnull=False, conversation_id__in=conversation_ids).all()
    for tweet in tweets:
        if tweet.tw_author is None:
            continue
        tweet_record = {"tweet_id": tweet.id, "text": tweet.text, "conversation_id": tweet.conversation_id,
                        "author_id": tweet.tw_author.id}
        metrics = tweet.tw_author.conversationauthormetrics_set.filter(
            conversation_id=tweet.conversation_id)
        if not metrics.exists():
            continue
        else:
            author_metrics = metrics.get()
            tweet_record["centrality"] = author_metrics.centrality
            tweet_record["baseline_vision"] = author_metrics.baseline_vision
            tweet_record["n_posts"] = author_metrics.n_posts
            records.append(tweet_record)

"""
from delab.api.api_util import get_all_conversation_ids
from delab.models import ConversationAuthorMetrics


def run():
    conversation_ids = get_all_conversation_ids()
    metrics = ConversationAuthorMetrics.objects.filter(conversation_id__in=conversation_ids).raw(
        "SELECT cam.id, dt.id as tweet_id, cam.conversation_id, cam.author_id, text, dt.twitter_id, "
        "is_toxic, toxic_value, n_posts, "
        "centrality, baseline_vision, n_posts, is_root_author "
        "FROM delab_tweet dt join delab_conversationauthormetrics cam "
        "on dt.conversation_id = cam.conversation_id and dt.tw_author_id = cam.author_id")
    for tweet in metrics:
        tweet_record = {"tweet_id": tweet.tweet_id, "text": tweet.text, "conversation_id": tweet.conversation_id,
                        "author_id": tweet.author_id, "centrality": tweet.centrality,
                        "baseline_vision": tweet.baseline_vision, "n_posts": tweet.n_posts}
        print(tweet_record)
        break
