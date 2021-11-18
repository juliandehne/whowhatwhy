import datetime

from delab.tw_connection_util import get_praw
from delab.models import TweetAuthor, Tweet, PLATFORM, SimpleRequest, TwTopic
from util.abusing_strings import convert_to_hash

"""
get the moderators like this
https://praw.readthedocs.io/en/stable/code_overview/other/subredditmoderation.html

for message in reddit.subreddit("mod").mod.inbox(limit=5):
    print(f"From: {message.author}, Body: {message.body}")
    for reply in message.replies:
        print(f"From: {reply.author}, Body: {reply.body}")

"""


# def get_moderators(topic_string, reddit):
#    subreddit = reddit.subreddit(topic_string)
#    moderator_queue = subreddit.modmail


def download_conversations_reddit(topic_string, simple_request_id):
    # create the topic and save it to the db
    simple_request, topic = get_simple_request(simple_request_id, topic_string)

    reddit = get_praw()
    author_counter = 0
    tweet_counter = 0

    for submission in reddit.subreddit(topic_string).hot(limit=2):
        submission.comments.replace_more(limit=None)
        save_reddit_entry(author_counter, submission, simple_request, submission, topic, tweet_counter,
                          is_comment=False)
        # moderators = get_moderators(topic_string, reddit)
        for comment in submission.comments.list():
            try:
                save_reddit_entry(author_counter, comment, simple_request, submission, topic, tweet_counter)
            except AttributeError:
                print("could not save comment {} to database".format(comment))
    print("created {} authors and {} tweets ".format(author_counter, tweet_counter))


def save_reddit_entry(author_counter, comment, simple_request, submission, topic, tweet_counter, is_comment=True):
    author_id = convert_to_hash(comment.author.id)
    created_time = datetime.datetime.fromtimestamp(comment.created)
    # create the author
    author, created = TweetAuthor.objects.get_or_create(
        twitter_id=author_id,
        name=comment.author.name,
        screen_name=comment.author.fullname,
        platform=PLATFORM.REDDIT
    )
    if created:
        author_counter += 1
    if is_comment:
        tweet_id = convert_to_hash(comment.id)
    else:
        tweet_id = convert_to_hash(comment.selftext)
    tn_parent = None
    conversation_id = convert_to_hash(submission.id)
    if is_comment:
        parent_id = comment.parent_id.split("_")[1]
        tn_parent = convert_to_hash(parent_id)
        if tn_parent == conversation_id:
            # if the comments are in the second hierarchy level the id should be the generated root id for that conversation
            tn_parent = Tweet.objects.filter(conversation_id=conversation_id, tn_parent__isnull=True).get().twitter_id
    try:
        in_reply_to_user_id = Tweet.objects.filter(twitter_id=tn_parent).get().author_id
    except Tweet.DoesNotExist:
        in_reply_to_user_id = None
    # create the tweet
    if is_comment:
        text = comment.body
    else:
        text = comment.title + "\n" + comment.selftext
    tweet, tweet_created = Tweet.objects.get_or_create(
        twitter_id=tweet_id,
        text=text,
        author_id=author_id,
        tn_parent=tn_parent,
        in_reply_to_user_id=in_reply_to_user_id,
        language=submission.subreddit.lang,
        platform=PLATFORM.REDDIT,
        created_at=created_time,
        conversation_id=conversation_id,
        simple_request=simple_request,
        topic=topic,
        tw_author=author
    )
    if tweet_created:
        tweet_counter += 1


def get_simple_request(simple_request_id, topic_string):
    topic, created = TwTopic.objects.get_or_create(
        title=topic_string
    )
    # save the request to the db in order to link the results in the view to the hashtags entered
    if simple_request_id > 0:
        simple_request, created = SimpleRequest.objects.get_or_create(
            pk=simple_request_id,
            topic=topic
        )
    else:
        request_string = "reddit top x submissions"
        simple_request, created = SimpleRequest.objects.get_or_create(
            title=request_string
        )
    return simple_request, topic
