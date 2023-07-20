import datetime
import logging

import prawcore
import pytz

from delab.corpus.DelabTreeDAO import persist_recursive_tree, set_up_topic_and_simple_request, \
    check_general_tree_requirements
from delab.corpus.filter_conversation_trees import solve_orphans
from delab.delab_enums import PLATFORM
from delab.models import TweetAuthor, Tweet
from delab.tw_connection_util import get_praw
from delab_trees.delab_tree import DelabTree
from delab_trees.recursive_tree.recursive_tree import TreeNode
from django_project.settings import MAX_CANDIDATES_REDDIT
from util.abusing_strings import convert_to_hash
from delab.delab_enums import LANGUAGE

"""
get the moderators like this
https://praw.readthedocs.io/en/stable/code_overview/other/subredditmoderation.html

for message in reddit.subreddit("mod").mod.inbox(limit=5):
    print(f"From: {message.author}, Body: {message.body}")
    for reply in message.replies:
        print(f"From: {reply.author}, Body: {reply.body}")

"""

logger = logging.getLogger(__name__)


def search_r_all(sub_reddit_string: str, simple_request_id: int, topic_string: str, tweet_filter=None, recent=True,
                 language=LANGUAGE.ENGLISH):
    simple_request, topic = set_up_topic_and_simple_request(sub_reddit_string, simple_request_id, topic_string)
    reddit = get_praw()
    try:
        if recent:
            for submission in reddit.subreddit("all").search(query=sub_reddit_string, limit=MAX_CANDIDATES_REDDIT,
                                                             sort="new"):
                save_reddit_tree(simple_request, submission, topic, language)
        else:
            for submission in reddit.subreddit("all").search(query=sub_reddit_string, limit=MAX_CANDIDATES_REDDIT):
                save_reddit_tree(simple_request, submission, topic, language)

    except prawcore.exceptions.Redirect:
        logger.error("reddit with this name does not exist")


def download_subreddit(sub_reddit_string, simple_request_id, topic_string=None, language=LANGUAGE.ENGLISH):
    if topic_string is None:
        topic_string = sub_reddit_string
    # create the topic and save it to the db,
    # creates a reddit specific dummy request (as there is no query when downloading a wholoe subrreddit
    simple_request, topic = set_up_topic_and_simple_request(sub_reddit_string, simple_request_id, topic_string)

    reddit = get_praw()

    try:
        for submission in reddit.subreddit(sub_reddit_string).hot(limit=10):
            save_reddit_tree(simple_request, submission, topic, language)
    except prawcore.exceptions.Redirect:
        logger.error("reddit with this name does not exist")


def save_reddit_tree(simple_request, submission, topic, language):
    root = compute_reddit_tree(submission, language)
    delab_tree = DelabTree.from_recursive_tree(root)
    if check_general_tree_requirements(delab_tree, verbose=False, platform=PLATFORM.REDDIT):
        persist_recursive_tree(root, PLATFORM.REDDIT, simple_request, topic)


def compute_reddit_tree(submission, language):
    comments = sort_comments_for_db(submission)

    # root node
    author_id, author_name = compute_author_id(submission)
    tree_id = convert_to_hash(submission.fullname)
    root_node_id = convert_to_hash(submission.fullname)
    if hasattr(submission, 'lang'):
        submission_lang = submission.lang
    else:
        submission_lang = language
    data = {
        "tree_id": tree_id,
        "post_id": root_node_id,
        "text": submission.title + "\n" + submission.selftext,
        "author_id": author_id,
        "created_at": convert_time_stamp_to_django(submission),
        "tw_author__name": author_name,
        "rd_data": submission,
        "lang": submission_lang,
        "url": "https://reddit.com" + submission.permalink,
        "reddit_id": submission.id}
    root = TreeNode(data, root_node_id, tree_id=tree_id)
    orphans = []

    for comment in comments:
        # node_id = comment.id
        node_id = convert_to_hash(comment.fullname)
        # parent_id = comment.parent_id.split("_")[1]
        parent_id = convert_to_hash(comment.parent_id)
        comment_author_id, comment_author_name = compute_author_id(comment)
        if hasattr(comment, 'lang'):
            comment_lang = comment.lang
        else:
            comment_lang = language
        comment_data = {
            "tree_id": tree_id,
            "post_id": node_id,
            "text": comment.body,
            "author_id": comment_author_id,
            "tw_author__name": comment_author_name,
            "created_at": convert_time_stamp_to_django(comment),
            "parent_id": parent_id,
            "rd_data": comment,
            "lang": comment_lang,
            "url": "https://reddit.com" + comment.permalink,
            "reddit_id": comment.id}
        node = TreeNode(comment_data, node_id, parent_id, tree_id=tree_id)
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
    return root


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


def convert_time_stamp_to_django(comment):
    created_time = datetime.datetime.fromtimestamp(comment.created_utc)
    amsterdam_timezone = pytz.timezone('Europe/Berlin')
    created_time = amsterdam_timezone.localize(created_time)
    return created_time


def compute_author_id(comment):
    name = "[deleted]"
    if comment.author is not None:
        if hasattr(comment.author, "name"):
            name = comment.author.name
    author_id = convert_to_hash(name)
    return author_id, name


def create_reddit_author(comment):
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


def download_conversations_by_id(conversation_ids: list[int], language=LANGUAGE.ENGLISH):
    tweets = Tweet.objects.filter(conversation_id__in=conversation_ids).filter(tn_parent__isnull=True).all()
    assert all(tweet.platform == PLATFORM.REDDIT for tweet in
               tweets), "can only download conversations like this for reddit posts"
    reddit = get_praw()
    for tweet in tweets:
        submission_url = tweet.original_url
        simple_request = tweet.simple_request
        topic = tweet.topic
        original_comment = reddit.submission(url=submission_url)
        recursive_tree = compute_reddit_tree(original_comment, language)
        persist_recursive_tree(recursive_tree, PLATFORM.REDDIT, simple_request, topic)
