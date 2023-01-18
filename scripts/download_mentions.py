from delab.api.api_util import get_all_twitter_conversation_ids
from delab.corpus.download_conversations_twitter import download_conversation_as_tree
from delab.corpus.download_exceptions import ConversationNotInRangeException
from delab.models import Mentions, TweetAuthor, Tweet
from delab.tw_connection_util import DelabTwarc


def run():
    twarc = DelabTwarc()
    conversation_ids = set(get_all_twitter_conversation_ids())
    c_with_downloaded_mentions = set(Mentions.objects.values_list("conversation_id", flat=True))
    conversation_ids = conversation_ids - c_with_downloaded_mentions
    for c_id in conversation_ids:
        try:
            c_tree = download_conversation_as_tree(twarc, c_id, 500, root_data=None)
        except ConversationNotInRangeException:
            continue
        mentions_map = retrieve_mentions(c_tree)
        for tweet_id, mentionee_ids in mentions_map.items():
            for mentionee_id in mentionee_ids:
                # store the mention in db
                try:
                    author = TweetAuthor.objects.filter(twitter_id=int(mentionee_id)).get()
                except Exception:
                    # print("could not find mentioned author in database")
                    continue
                try:
                    tweet_id = int(tweet_id)
                    tweet = Tweet.objects.filter(twitter_id=tweet_id).get()
                except Exception:
                    # print("could not find tweet in database")
                    continue
                if not Mentions.objects.filter(mentionee_id=mentionee_id, tweet_id=tweet_id).exists():
                    Mentions.objects.create(
                        conversation_id=int(c_id),
                        mentionee=author,
                        tweet=tweet
                    )


def retrieve_mentions(c_tree, result=None):
    if result is None:
        result = {}
    if not hasattr(c_tree, 'data'):
        return result
    data = c_tree.data
    result[data["id"]] = get_mentioned_ids(data)
    for child in c_tree.children:
        retrieve_mentions(child, result)
    return result


def get_mentioned_ids(twitter_payload):
    result = []
    if 'entities' in twitter_payload:
        if 'mentions' in twitter_payload["entities"]:
            mentions_payload = twitter_payload["entities"]["mentions"]
            for mention_payload in mentions_payload:
                result.append(mention_payload["id"])
    return result
