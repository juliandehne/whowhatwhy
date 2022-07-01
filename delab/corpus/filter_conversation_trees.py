from django.db.models import F
from django.forms.models import model_to_dict

from delab.TwConversationTree import TreeNode
from delab.api.api_util import ConversationFilter
from delab.models import Tweet


def get_conversation_trees(topic, conversation_id=None, conversation_filter: ConversationFilter = None) -> \
        [TreeNode]:
    """
    :param topic: the topic string
    :param conversation_id:  the conversation id
    :param conversation_filter: a utility class for filtering the conversations
    :return:
    """
    return convert_to_conversation_trees(conversation_id, topic)


def convert_to_conversation_trees(conversation_id=None, topic=None):
    objects = Tweet.objects.select_related("tw_author")

    if conversation_id is not None:
        if topic is not None:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True,
                                              conversation_id=conversation_id,
                                              topic__title=topic).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False,
                                                  topic__title=topic,
                                                  conversation_id=conversation_id).order_by('-created_at').all()]
        else:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True,
                                              conversation_id=conversation_id).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False,
                                                  conversation_id=conversation_id).order_by('-created_at').all()]
    else:
        if topic is not None:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True,
                                              topic__title=topic).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False,
                                                  topic__title=topic).order_by('-created_at').all()]
        else:
            roots_as_record = [author_tweet_to_records(tweet) for tweet in
                               objects.filter(tn_parent_id__isnull=True).all()]
            not_roots_as_record = [author_tweet_to_records(tweet) for tweet in
                                   objects.filter(tn_parent_id__isnull=False).order_by('-created_at').all()]
    return reconstruct_trees_from_records(not_roots_as_record, roots_as_record)


def author_tweet_to_records(tweet):
    result = model_to_dict(tweet)
    if tweet.tw_author is not None:
        result.update({"author_name": tweet.tw_author.name})
    else:
        result.update({"author_name": "unknown"})
    return result


def reconstruct_trees_from_records(not_roots_as_rec, roots_as_rec):
    trees_roots = {}
    not_roots = {}
    for root_data in roots_as_rec:
        root_node = TreeNode(root_data, root_data["twitter_id"], root_data["tn_parent"])
        trees_roots[root_data["conversation_id"]] = root_node
    # group tree elements based on their conversation id
    conversation_ids = set()
    for not_root in not_roots_as_rec:
        conversation_id = not_root["conversation_id"]
        conversation_ids.add(conversation_id)
        if conversation_id not in not_roots:
            not_roots[conversation_id] = [not_root]
        else:
            not_roots[conversation_id] = not_roots.get(conversation_id) + [not_root]
    for conversation_id in conversation_ids:
        if conversation_id in trees_roots:
            tree_node = trees_roots.get(conversation_id)
            orphans = []
            for not_root in not_roots[conversation_id]:
                to_add_node = TreeNode(not_root, not_root["twitter_id"], not_root["tn_parent"])
                orphans.append(to_add_node)
            # now solve all the orphans that have not been seen
            orphan_added = True
            while orphan_added:
                orphan_added, orphans = solve_orphans(orphans, tree_node)
            trees_roots[conversation_id] = tree_node
    return trees_roots


def solve_orphans(orphans, tree_node):
    if len(orphans) == 0:
        return False, []

    rest_orphans = []
    orphan_added = False
    for orphan in orphans:
        added = tree_node.find_parent_of(orphan)
        # either or the list es reduced by one element
        if not added:
            rest_orphans.append(orphan)
        # either nothing was found that False is returned stopping the cycle
        else:
            orphan_added = True
    if len(orphans) == len(rest_orphans):
        print(f"could not reconstruct faulty tree for conversation_id {orphans[0].data['conversation_id']}")
        # return False, []
    assert len(orphans) != len(rest_orphans)
    return orphan_added, rest_orphans
