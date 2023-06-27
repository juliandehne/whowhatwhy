import datetime
import logging

import prawcore
import pytz
from django.db import IntegrityError

from delab_trees.recursive_tree.recursive_tree import TreeNode
from delab.corpus.download_conversations_util import set_up_topic_and_simple_request, apply_tweet_filter
from delab.corpus.filter_conversation_trees import solve_orphans
from delab.delab_enums import PLATFORM, LANGUAGE
from delab.models import TweetAuthor, Tweet, SimpleRequest, TwTopic
from delab.tw_connection_util import get_praw
from django_project.settings import MAX_CANDIDATES_REDDIT, MAX_CONVERSATION_LENGTH, MIN_CONVERSATION_LENGTH
from util.abusing_strings import convert_to_hash

"""
get the moderators like this
https://praw.readthedocs.io/en/stable/code_overview/other/subredditmoderation.html

for message in reddit.subreddit("mod").mod.inbox(limit=5):
    print(f"From: {message.author}, Body: {message.body}")
    for reply in message.replies:
        print(f"From: {reply.author}, Body: {reply.body}")

"""

logger = logging.getLogger(__name__)


def search_r_all(sub_reddit_string: str, simple_request_id: int, topic_string: str,
                 max_number_of_candidates=MAX_CANDIDATES_REDDIT,
                 max_conversation_length=MAX_CONVERSATION_LENGTH,
                 min_conversation_length=MIN_CONVERSATION_LENGTH,
                 language=LANGUAGE.ENGLISH, tweet_filter=None, recent=True):
    simple_request, topic = set_up_topic_and_simple_request(sub_reddit_string, simple_request_id, topic_string)
    reddit = get_praw()
    try:
        if recent:
            for submission in reddit.subreddit("all").search(query=sub_reddit_string, limit=max_number_of_candidates,
                                                             sort="new"):
                save_reddit_tree(simple_request, submission, topic, min_conversation_length=min_conversation_length,
                                 max_conversation_length=max_conversation_length, tweetfilter=tweet_filter)
        else:
            for submission in reddit.subreddit("all").search(query=sub_reddit_string, limit=max_number_of_candidates):
                save_reddit_tree(simple_request, submission, topic, min_conversation_length=min_conversation_length,
                                 max_conversation_length=max_conversation_length, tweetfilter=tweet_filter)

    except prawcore.exceptions.Redirect:
        logger.error("reddit with this name does not exist")


def download_subreddit(sub_reddit_string, simple_request_id, topic_string=None):
    if topic_string is None:
        topic_string = sub_reddit_string
    # create the topic and save it to the db,
    # creates a reddit specific dummy request (as there is no query when downloading a wholoe subrreddit
    simple_request, topic = get_simple_request(simple_request_id, topic_string)
    reddit = get_praw()

    try:
        for submission in reddit.subreddit(sub_reddit_string).hot(limit=10):
            save_reddit_tree(simple_request, submission, topic)
    except prawcore.exceptions.Redirect:
        logger.error("reddit with this name does not exist")


def save_reddit_tree(simple_request, submission, topic, max_conversation_length=MAX_CONVERSATION_LENGTH,
                     min_conversation_length=MIN_CONVERSATION_LENGTH, tweetfilter=None):
    comments = sort_comments_for_db(submission)

    comment_dict, root = compute_reddit_tree(comments, submission)
    if root is not None:
        tree_size = root.flat_size()
        if min_conversation_length < tree_size < max_conversation_length:
            logger.debug("found suitable conversation in reddit with length {}".format(tree_size))
            conversation_id = convert_to_hash(submission.fullname)
            created = save_reddit_submission(submission, simple_request, topic, tweetfilter, conversation_id)
            if created:
                children = [child for child in root.children]
                for child in children:
                    save_reddit_node(child, comment_dict, simple_request, topic, tweetfilter, conversation_id)
            logger.debug(
                "saved {} reddit posts to db".format(Tweet.objects.filter(conversation_id=conversation_id).count()))
    else:
        logger.error("could not compute reddit_tree for conversation {}".format(submission))


def save_reddit_node(node: TreeNode, comment_dict, simple_request, topic, tweetfilter, conversation_id_check):
    comment = comment_dict[node.tree_id]
    created = save_reddit_entry(comment, simple_request, topic, tweetfilter, conversation_id_check)
    if created:
        for child in node.children:
            save_reddit_node(child, comment_dict, simple_request, topic, tweetfilter, conversation_id_check)
    else:
        # TODO: check if maybe a faulty comment can be skipped and attach all the children to the parent of the
        #  skipped comment
        logger.error("skipping tree with direct children {} and depth {}".format(len(node.children),
                                                                                 node.compute_max_path_length()))


def compute_reddit_tree(comments, submission):
    comment_dict = {}  # keys are the comment/submission ids and values are the praw objects associate
    # root node
    author_id, author_name = compute_author_id(submission)
    data = {"conversation_id": submission.fullname,
            "id": submission.fullname,
            "tree_id": submission.fullname,
            "post_id": submission.fullname,
            "text": submission.title + "\n" + submission.selftext,
            "author_id": author_id,
            "tw_author__name": author_name}
    root = TreeNode(data, submission.fullname)
    comment_dict[submission.fullname] = submission
    orphans = []
    for comment in comments:
        # node_id = comment.id
        node_id = comment.fullname
        comment_dict[node_id] = comment
        # parent_id = comment.parent_id.split("_")[1]
        parent_id = comment.parent_id
        node = TreeNode(comment, node_id, parent_id)
        # IF NODE CANNOT BE PLACED IN TREE, ORPHAN IT UNTIL ITS PARENT IS FOUND
        if not root.find_parent_of(node):
            orphans.append(node)
    # logger.info('{} orphaned tweets for conversation {} before resolution'.format(len(orphans), submission.id))
    orphan_added = True
    while orphan_added:
        orphan_added, orphans = solve_orphans(orphans, root)
    if len(orphans) > 0:
        logger.error('{} orphaned tweets for conversation {}'.format(len(orphans), submission.fullname))
        logger.error('{} downloaded tweets'.format(len(comments)))
    return comment_dict, root


def sort_comments_for_db(submission):
    submission.comments.replace_more(limit=None)
    result = []
    for comment in submission.comments.list():
        result.append(comment)
    if len(result) > 3:
        pass
    # l_original_comments = len(comments)
    # missing = [comment for comment in comments if hasattr(comment, 'MISSING_COMMENT_MESSAGE')]
    # comments = [comment for comment in comments if not hasattr(comment, 'MISSING_COMMENT_MESSAGE')]
    result.sort(key=lambda x: x.created)
    # logger.debug("{}/{} comments in tree are missing".format(len(missing), l_original_comments))
    # if len(comments) > 0:
    #    print("found tree")
    return result


def save_reddit_entry(comment, simple_request, topic, tweetfilter, conversation_id_check):
    try:

        created_time = convert_time_stamp_to_django(comment)
        # create the author
        author_id, name = compute_author_id(comment)

        if TweetAuthor.objects.filter(twitter_id=author_id).exists():
            author = TweetAuthor.objects.filter(twitter_id=author_id).first()
        else:
            author, created = TweetAuthor.objects.get_or_create(
                twitter_id=author_id,
                name=name,
                screen_name=name,
                platform=PLATFORM.REDDIT
            )

        # tweet_id = convert_to_hash(comment.id)
        tweet_id = convert_to_hash(comment.fullname)
        banned_at = None
        if comment.banned_at_utc:
            banned_at = datetime.datetime.fromtimestamp(comment.banned_at_utc)

        conversation_id = convert_to_hash(comment.submission.fullname)
        assert conversation_id_check == conversation_id

        # parent_id = comment.parent_id.split("_")[1]
        parent_id = comment.parent_id
        tn_parent = convert_to_hash(parent_id)
        if tn_parent == conversation_id:
            # if the comments are in the second hierarchy level the id should be the generated root id for that
            # conversation
            try:
                tn_parent = Tweet.objects.filter(conversation_id=conversation_id,
                                                 tn_parent__isnull=True).get().twitter_id
            except Exception as ex:
                logger.error("could not find parent in second hierarchy TODO DEBUG {}".format(ex))
                return False
        # create the tweet
        text = comment.body
        language = comment.submission.subreddit.lang
        if Tweet.objects.filter(twitter_id=tweet_id).exists():
            return True
        try:
            tweet = Tweet(
                twitter_id=tweet_id,
                text=text,
                author_id=author_id,
                tn_parent_id=tn_parent,
                language=language,
                platform=PLATFORM.REDDIT,
                created_at=created_time,
                conversation_id=conversation_id,
                simple_request=simple_request,
                topic=topic,
                tw_author=author,
                banned_at=banned_at,
                reddit_id=comment.fullname
            )
            apply_tweet_filter(tweet, tweetfilter)
            return True
        except IntegrityError as ex:
            logger.error("could not save reddit comment to db because of {}".format(ex))
            return False
        except pytz.exceptions.AmbiguousTimeError:
            logger.error("something was weird with the time field")
            return False
    except prawcore.exceptions.NotFound:
        logger.error("could not find something on reddit anymore")


def convert_time_stamp_to_django(comment):
    created_time = datetime.datetime.fromtimestamp(comment.created_utc)
    amsterdam_timezone = pytz.timezone('Europe/Berlin')
    created_time = amsterdam_timezone.localize(created_time)
    return created_time


def save_reddit_submission(comment, simple_request, topic, tweetfilter, conversation_id_check):
    author_id, name = compute_author_id(comment)
    created_time = convert_time_stamp_to_django(comment)
    banned_at = None
    # create the author
    if TweetAuthor.objects.filter(twitter_id=author_id).exists():
        author = TweetAuthor.objects.filter(twitter_id=author_id).first()
    else:
        author, created = TweetAuthor.objects.get_or_create(
            twitter_id=author_id,
            name=name,
            screen_name=name,
            platform=PLATFORM.REDDIT
        )
    # tweet_id = convert_to_hash(comment.selftext)
    tweet_id = convert_to_hash(comment.fullname)
    # conversation_id = convert_to_hash(comment.id)
    conversation_id = convert_to_hash(comment.fullname)
    assert conversation_id_check == conversation_id

    text = comment.title + "\n" + comment.selftext

    language = comment.subreddit.lang
    try:
        tweet = Tweet(
            twitter_id=tweet_id,
            text=text,
            author_id=author_id,
            language=language,
            platform=PLATFORM.REDDIT,
            created_at=created_time,
            conversation_id=conversation_id,
            simple_request=simple_request,
            topic=topic,
            tw_author=author,
            banned_at=banned_at,
            reddit_id=comment.fullname
        )
        apply_tweet_filter(tweet, tweetfilter)
        return True
    except IntegrityError as ex:
        logger.error("could not save submission because {}".format(ex))
        return False
    except pytz.exceptions.AmbiguousTimeError:
        "something was weird with the time field"
        return False


def compute_author_id(comment):
    name = "[deleted]"
    if comment.author is not None:
        if hasattr(comment.author, "name"):
            name = comment.author.name
    author_id = convert_to_hash(name)
    return author_id, name


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
