import logging
import re
import time

from django.db import IntegrityError
from requests import HTTPError

from delab.TwConversationTree import TreeNode
from delab.corpus.download_conversations_util import set_up_topic_and_simple_request, apply_tweet_filter

from delab.corpus.download_exceptions import ConversationNotInRangeException
from delab.corpus.filter_conversation_trees import solve_orphans
from delab.delab_enums import PLATFORM, LANGUAGE, TWEET_RELATIONSHIPS
from delab.models import Tweet, TwTopic, SimpleRequest
from delab.tw_connection_util import DelabTwarc
from django_project.settings import MAX_CANDIDATES, MAX_CONVERSATION_LENGTH, MIN_CONVERSATION_LENGTH
from util.abusing_lists import powerset

logger = logging.getLogger(__name__)


def download_conversations_tw(topic_string, query_string, request_id=-1, language=LANGUAGE.ENGLISH, max_data=False,
                              fast_mode=False, conversation_filter=None, tweet_filter=None, platform=PLATFORM.TWITTER,
                              recent=True,
                              max_conversation_length=MAX_CONVERSATION_LENGTH,
                              min_conversation_length=MIN_CONVERSATION_LENGTH,
                              max_number_of_candidates=MAX_CANDIDATES):
    if query_string is None or query_string.strip() == "":
        return False
    """
    :param recent: use the recent api from twitter which is faster and more current
    :param topic_string:
    :param query_string:
    :param request_id:
    :param language:
    :param max_data:
    :param fast_mode:
    :param conversation_filter:
    :param tweet_filter:
    :param platform:
    :return:
    """

    simple_request, topic = set_up_topic_and_simple_request(query_string, request_id, topic_string)

    twarc = DelabTwarc()

    # download the conversations
    if max_data:
        # this computes the powerset of the queried words
        pattern = r'[\(\)\[\]]'
        bag_of_words = re.sub(pattern, '', query_string).split(" ")
        combinations = list(powerset(bag_of_words))
        combinations_l = len(combinations) - 1
        combination_counter = 0
        for hashtag_set in combinations:
            if len(hashtag_set) > 0:
                combination_counter += 1
                new_query = " ".join(hashtag_set)
                filter_conversations(twarc, new_query, topic, simple_request, platform, language=language,
                                     fast_mode=fast_mode, conversation_filter=conversation_filter,
                                     tweet_filter=tweet_filter, recent=recent,
                                     max_conversation_length=max_conversation_length,
                                     min_conversation_length=min_conversation_length,
                                     max_number_of_candidates=max_number_of_candidates)
                logger.debug("FINISHED combination {}/{}".format(combination_counter, combinations_l))
    else:
        # in case max_data is false we don't compute the powerset of the hashtags
        filter_conversations(twarc, query_string, topic, simple_request, platform, language=language,
                             fast_mode=fast_mode, conversation_filter=conversation_filter,
                             tweet_filter=tweet_filter, recent=recent, max_conversation_length=max_conversation_length,
                             min_conversation_length=min_conversation_length,
                             max_number_of_candidates=max_number_of_candidates)


def filter_conversations(twarc,
                         query,
                         topic,
                         simple_request,
                         platform,
                         max_conversation_length=MAX_CONVERSATION_LENGTH,
                         min_conversation_length=MIN_CONVERSATION_LENGTH,
                         language=LANGUAGE.ENGLISH,
                         max_number_of_candidates=MAX_CANDIDATES,
                         fast_mode=False,
                         conversation_filter=None,
                         tweet_filter=None, recent=True):
    """
    :param recent:
    :param twarc:
    :param query:
    :param topic:
    :param simple_request:
    :param platform:
    :param max_conversation_length:
    :param min_conversation_length:
    :param language:
    :param max_number_of_candidates:
    :param fast_mode:
    :param conversation_filter:
    :param tweet_filter:
    :return:
    """

    candidates, n_pages = download_conversation_representative_tweets(twarc, query, max_number_of_candidates, language,
                                                                      recent=recent)

    downloaded_tweets = 0
    n_dismissed_candidates = 0
    # tweet_lookup_request_counter = 250
    # if recent:
    #    tweet_lookup_request_counter = 400

    for candidate in candidates:
        # assert that not more then tweets quota is downloaded
        # tweet_lookup_request_counter = ensuring_tweet_lookup_quota(n_pages, recent, tweet_lookup_request_counter)
        # tweet_lookup_request_counter -= 1
        # assert that the conversation is long enough
        try:
            reply_count = candidate["public_metrics"]["reply_count"]

            if (min_conversation_length / 2) < reply_count < max_conversation_length:
                logger.debug("selected candidate tweet {}".format(candidate))
                conversation_id = candidate["conversation_id"]

                root_node = download_conversation_as_tree(twarc, conversation_id, max_conversation_length)

                if conversation_filter is not None:
                    root_node = conversation_filter(root_node)

                if root_node is None:
                    logger.error("found conversation_id that could not be processed")
                    continue
                else:
                    flat_tree_size = root_node.flat_size()
                    # tweet_lookup_request_counter -= flat_tree_size
                    logger.debug("found tree with size: {}".format(flat_tree_size))
                    logger.debug("found tree with depth: {}".format(root_node.compute_max_path_length()))
                    downloaded_tweets += flat_tree_size
                    if min_conversation_length < flat_tree_size < max_conversation_length:
                        save_tree_to_db(root_node, topic, simple_request, conversation_id, platform,
                                        tweet_filter=tweet_filter)
                        logger.debug("found suitable conversation and saved to db {}".format(conversation_id))
                        # for debugging you can ascii art print the downloaded conversation_tree
                        # root_node.print_tree(0)
            else:
                n_dismissed_candidates += 1
        except ConversationNotInRangeException as ex:
            n_dismissed_candidates += 1
            logger.debug("conversation was dismissed because it was longer than {}".format(max_conversation_length))
    logger.debug("{} of {} candidates were dismissed".format(n_dismissed_candidates, len(candidates)))


def ensuring_tweet_lookup_quota(n_pages, recent, tweet_lookup_request_counter):
    if tweet_lookup_request_counter - n_pages <= 0:
        tweet_lookup_request_counter = 250
        if recent:
            tweet_lookup_request_counter = 400
        logger.error("going to sleep between processing candidates because of rate limitations")
        time.sleep(300 * 60)
    return tweet_lookup_request_counter


def download_conversation_representative_tweets(twarc, query, n_candidates,
                                                language=LANGUAGE.ENGLISH, recent=True):
    """
    :param recent:
    :param twarc:
    :param query:
    :param n_candidates:
    :param language:
    :return:
    """
    min_page_size = 10
    max_page_size = 500
    if n_candidates > max_page_size:
        page_size = 500
    else:
        page_size = n_candidates
    assert page_size >= min_page_size

    twitter_accounts_query = query + " lang:" + language
    logger.debug(twitter_accounts_query)
    candidates = []
    try:
        if recent:
            page_size = 100
            candidates = twarc.search_recent(query=twitter_accounts_query,
                                             tweet_fields="conversation_id,author_id,public_metrics")
        else:
            candidates = twarc.search_all(query=twitter_accounts_query,
                                          tweet_fields="conversation_id,author_id,public_metrics",
                                          max_results=page_size)
    except HTTPError as httperror:
        print(httperror)
    result = []
    n_pages = 1
    for candidate in candidates:
        result += candidate.get("data", [])
        n_pages += 1
        # logger.debug("number of candidates downloaded: {}".format(str(count)))
        if n_pages * page_size > n_candidates:
            break

    return result, n_pages


def download_conversation_as_tree(twarc, conversation_id, max_replies, root_data=None):
    if root_data is None:
        results = next(twarc.tweet_lookup(tweet_ids=[conversation_id]))
        root_data = results["data"][0]
    return create_tree_from_raw_tweet_stream(conversation_id, max_replies, root_data, twarc)


def create_tree_from_raw_tweet_stream(conversation_id, max_replies, root_data, twarc):
    tweets = []
    for result in twarc.search_all("conversation_id:{}".format(conversation_id)):
        tweets = tweets + result.get("data", [])
        check_conversation_max_size(max_replies, tweets)
    root, orphans = create_conversation_tree_from_tweet_data(conversation_id, root_data, tweets)
    return root


def create_conversation_tree_from_tweet_data(conversation_id, root_tweet, tweets):
    # sort tweets by creation date in order to speed up the tree construction
    tweets.sort(key=lambda x: x["created_at"], reverse=False)
    root = TreeNode(root_tweet, root_tweet["id"])
    orphans = []
    for item in tweets:
        # node_id = item["author_id"]
        # parent_id = item["in_reply_to_user_id"]
        node_id = int(item["id"])
        parent_id, parent_type = get_priority_parent_from_references(item["referenced_tweets"])
        # parent_id = item["referenced_tweets.id"]
        node = TreeNode(item, node_id, parent_id, parent_type=parent_type)
        # IF NODE CANNOT BE PLACED IN TREE, ORPHAN IT UNTIL ITS PARENT IS FOUND
        if not root.find_parent_of(node):
            orphans.append(node)
    logger.info('{} orphaned tweets for conversation {} before resolution'.format(len(orphans), conversation_id))
    orphan_added = True
    while orphan_added:
        orphan_added, orphans = solve_orphans(orphans, root)
    if len(orphans) > 0:
        logger.error('{} orphaned tweets for conversation {}'.format(len(orphans), conversation_id))
        logger.error('{} downloaded tweets'.format(len(tweets)))
    return root, orphans


def check_conversation_max_size(max_replies, tweets):
    conversation_size = len(tweets)
    if conversation_size >= max_replies > 0:
        raise ConversationNotInRangeException(conversation_size)


def get_priority_parent_from_references(references):
    reference_types = [ref["type"] for ref in references]
    replied_tos = [int(ref["id"]) for ref in references if ref["type"] == TWEET_RELATIONSHIPS.REPLIED_TO]
    retweeted_tos = [int(ref["id"]) for ref in references if ref["type"] == TWEET_RELATIONSHIPS.RETWEETED]
    quoted_tos = [int(ref["id"]) for ref in references if ref["type"] == TWEET_RELATIONSHIPS.QUOTED]
    if TWEET_RELATIONSHIPS.REPLIED_TO in reference_types:
        return replied_tos[0], TWEET_RELATIONSHIPS.REPLIED_TO
    if TWEET_RELATIONSHIPS.QUOTED in reference_types:
        return quoted_tos[0], TWEET_RELATIONSHIPS.QUOTED
    if TWEET_RELATIONSHIPS.RETWEETED in reference_types:
        return retweeted_tos[0], TWEET_RELATIONSHIPS.RETWEETED
    raise Exception("no parent found")


def save_tree_to_db(root_node: TreeNode,
                    topic: TwTopic,
                    simple_request: SimpleRequest,
                    conversation_id: int,
                    platform: PLATFORM,
                    tweet_filter=None):
    """ This method persist a conversation tree in the database
        Parameters
        ----------
        :param root_node : TwConversationTree
        :param topic : the topic of the query
        :param simple_request: the query string in order to link the view
        :param conversation_id: the conversation id of the candidate tweet that was found with the request
        :param platform: this was added to allow for a "fake" delab platform to come in
        :param tweet_filter: a function that takes a tweet model object and validates it (returns None if not)

    """
    store_tree_data(conversation_id, platform, root_node, simple_request, topic, tweet_filter)
    # run some tree validations


def store_tree_data(conversation_id: int, platform: PLATFORM, root_node: TreeNode, simple_request: SimpleRequest,
                    topic: TwTopic, tweet_filter):
    # before = dt.now()
    tweet = Tweet(topic=topic,
                  text=root_node.data["text"],
                  simple_request=simple_request,
                  twitter_id=root_node.data["id"],
                  author_id=root_node.data["author_id"],
                  conversation_id=conversation_id,
                  created_at=root_node.data["created_at"],
                  in_reply_to_user_id=root_node.data.get("in_reply_to_user_id", None),
                  in_reply_to_status_id=root_node.data.get("in_reply_to_status_id", None),
                  platform=platform,
                  tn_parent_id=root_node.parent_id,
                  tn_parent_type=root_node.parent_type,
                  # tn_priority=priority,
                  language=root_node.data["lang"])
    try:
        apply_tweet_filter(tweet, tweet_filter)
    except IntegrityError:
        pass
    # after = dt.now()
    # logger.debug("a query took: {} milliseconds".format((after - before).total_seconds() * 1000))
    # recursively persisting the children in the database
    if not len(root_node.children) == 0:
        for child in root_node.children:
            store_tree_data(conversation_id, platform, child, simple_request, topic, tweet_filter)
