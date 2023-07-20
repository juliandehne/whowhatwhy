import logging

from django.db import IntegrityError

from delab.corpus.download_conversations_util import apply_tweet_filter
from delab.delab_enums import PLATFORM
from delab.models import SimpleRequest, TwTopic, Tweet
from delab_trees import TreeNode
from delab_trees.delab_tree import DelabTree
from django_project.settings import MIN_CONVERSATION_LENGTH, MIN_CONVERSATION_DEPTH, MAX_CONVERSATION_LENGTH, \
    MAX_CONVERSATION_LENGTH_REDDIT, MIN_CONVERSATION_LENGTH_MASTODON, MIN_CONVERSATION_DEPTH_MASTODON

logger = logging.getLogger(__name__)


def persist_tree(tree: DelabTree, platform: PLATFORM, simple_request: SimpleRequest = None,
                 topic: TwTopic = None, candidate_id: int = -1, tweet_filter=None):
    root_node = tree.as_recursive_tree()
    persist_recursive_tree(root_node, platform, simple_request, topic, candidate_id, tweet_filter)


def persist_recursive_tree(root_node: TreeNode, platform: PLATFORM, simple_request: SimpleRequest,
                           topic: TwTopic, candidate_id: int = -1, tweet_filter=None):
    # before = dt.now()
    simple_request, topic = generate_default_request_and_topic(simple_request, topic)
    conversation_id = root_node.data["tree_id"]
    if type(root_node.data["post_id"]) != 'float':
        float(root_node.data["post_id"])
    twitter_id = int(root_node.data["post_id"])
    url = None
    if "url" in root_node.data:
        url = root_node.data["url"]
    reddit_id = None
    if "reddit_id" in root_node.data:
        reddit_id = root_node.data["reddit_id"]
    tweet = Tweet(topic=topic,
                  text=root_node.data["text"],
                  simple_request=simple_request,
                  twitter_id=twitter_id,
                  author_id=int(root_node.data["author_id"]),
                  conversation_id=int(conversation_id),
                  created_at=root_node.data["created_at"],
                  in_reply_to_user_id=root_node.data.get("in_reply_to_user_id", None),
                  in_reply_to_status_id=root_node.data.get("in_reply_to_status_id", None),
                  platform=platform,
                  tn_parent_id=root_node.parent_id,
                  tn_parent_type=root_node.parent_type,
                  was_query_candidate=candidate_id == twitter_id,
                  # tn_priority=priority,
                  language=root_node.data["lang"],
                  original_url=url,
                  reddit_id=reddit_id)
    try:
        apply_tweet_filter(tweet, tweet_filter)
    except IntegrityError as ex:
        # logger.debug(ex)
        pass
    # after = dt.now()
    # logger.debug("a query took: {} milliseconds".format((after - before).total_seconds() * 1000))
    # recursively persisting the children in the database
    if not len(root_node.children) == 0:
        for child in root_node.children:
            persist_recursive_tree(child, platform, simple_request, topic, candidate_id, tweet_filter)


def check_general_tree_requirements(delab_tree: DelabTree, verbose=False, platform=PLATFORM.REDDIT):
    if delab_tree is not None:
        tree_size = delab_tree.total_number_of_posts()
        tree_depth = delab_tree.depth()
        min_conversation_length = MIN_CONVERSATION_LENGTH
        min_depth = MIN_CONVERSATION_DEPTH
        max_conversation_length = MAX_CONVERSATION_LENGTH
        if platform == PLATFORM.REDDIT:
            max_conversation_length = MAX_CONVERSATION_LENGTH_REDDIT
        if platform == PLATFORM.MASTODON:
            min_conversation_length = MIN_CONVERSATION_LENGTH_MASTODON
            min_depth = MIN_CONVERSATION_DEPTH_MASTODON
        if min_conversation_length < tree_size < max_conversation_length and tree_depth >= min_depth:
            if verbose:
                logger.debug("found suitable conversation with length {} and depth {}".format(tree_size, tree_depth))
            return True
        return False
    else:
        if verbose:
            logger.error("could not check tree requirements for NoneType")
        return False


def set_up_topic_and_simple_request(query_string, request_id, topic_string):
    # save the request to the db in order to link the results in the view to the hashtags entered
    if SimpleRequest.objects.filter(title=query_string).exists():
        simple_request = SimpleRequest.objects.filter(title=query_string).get()
        topic = simple_request.topic
    else:
        # create the topic and save it to the db
        topic, created = TwTopic.objects.get_or_create(
            title=topic_string
        )
        if request_id > 0:
            simple_request, created = SimpleRequest.objects.get_or_create(
                pk=request_id,
                topic=topic
            )
        else:
            # request_string = "#" + ' #'.join(hashtags)
            simple_request, created = SimpleRequest.objects.get_or_create(
                title=query_string,
                topic=topic
            )
    return simple_request, topic


def generate_default_request_and_topic(simple_request, topic):
    if topic is None:
        # create the topic and save it to the db
        topic, created = TwTopic.objects.get_or_create(
            title="topic not given"
        )

    if simple_request is None:
        simple_request, created = SimpleRequest.objects.get_or_create(
            title="query not given",
            topic=topic
        )
    return simple_request, topic
