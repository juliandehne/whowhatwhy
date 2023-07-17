import logging
import timeit
from functools import partial

from django.db import IntegrityError
from django.utils import timezone

from delab.corpus.DelabTreeDAO import check_general_tree_requirements, persist_tree, set_up_topic_and_simple_request
from delab.corpus.download_conversations_proxy import download_daily_sample
from delab.delab_enums import PLATFORM
from delab.models import Tweet, ConversationFlow
from delab_trees import TreeManager
from delab_trees.delab_post import DelabPost
from delab_trees.flow_duos import compute_flow_name

logger = logging.getLogger(__name__)

M_TURK_TOPIC = "mturk_candidate"


def download_mturk_sample_conversations(n_runs, platform, min_results, persist=True):
    # Perform 100 runs of the function and measure the time taken

    download_mturk_sample_helper = partial(download_mturk_samples, platform, min_results, persist)
    execution_time = timeit.timeit(download_mturk_sample_helper, number=n_runs)
    average_time = (execution_time / 100) / 60
    print("Execution time:", execution_time, "seconds")
    print("Average Execution time:", average_time, "minutes")


def download_mturk_samples(platform, min_results, persist) -> list[list[DelabPost]]:
    result = []
    flow_result_count = 0
    # print("downloading random conversations for mturk_labeling")
    while flow_result_count < min_results:
        downloaded_trees = download_daily_sample(topic_string=M_TURK_TOPIC, platform=platform)
        validated_trees = []
        # reddit sampler has integrated validation
        if platform != PLATFORM.REDDIT:
            for tree in downloaded_trees:
                validated = tree.validate(verbose=False)
                useful = check_general_tree_requirements(tree, platform=platform)
                if validated and useful:
                    validated_trees.append(tree)
        else:
            validated_trees = downloaded_trees

        if len(validated_trees) > 0:
            forest = TreeManager.from_trees(validated_trees)

            flow_sample: list[list[DelabPost]] = forest.get_flow_sample(5, filter_function=meta_list_filter)
            if flow_sample is not None and len(flow_sample) > 0:
                logging.debug("found flows {}".format(len(flow_sample)))
                result += flow_sample

                # collect ids of the trees from the sample
                sample_tree_ids = []
                for sample in flow_sample:
                    first_post = sample[0]
                    tree_id = first_post.tree_id
                    sample_tree_ids.append(tree_id)
                # throw out the trees not sampled
                forest.keep(sample_tree_ids)

                # potentially remove even more samples here using Valentins IPA
                if persist:
                    for tree_id, tree in forest.trees.items():
                        query_string = platform + "" + str(timezone.now().date()) + "mturk_sample"
                        simple_request, topic = set_up_topic_and_simple_request(query_string, -1, M_TURK_TOPIC)
                        persist_tree(tree, platform, simple_request, topic)
                    objects = Tweet.objects.filter(conversation_id__in=sample_tree_ids).values_list("conversation_id",
                                                                                                    flat=True)
                    n_stored_objects = len(set(list(objects)))
                    n_sample_tree_ids = len(set(sample_tree_ids))
                    assert n_stored_objects == n_sample_tree_ids
                    duplicated_count = persist_flow_in_db(flow_sample)
                    new_flows_persisted = len(flow_sample) - duplicated_count
                    logger.debug("persisted in database: {}".format(new_flows_persisted))
                    flow_result_count += new_flows_persisted
                else:
                    flow_result_count = len(result)
    return result


def persist_flow_in_db(flow_sample: list[list[DelabPost]]):
    dublicated_count = 0
    for flow in flow_sample:
        try:
            tweet_ids = list(map(lambda x: x.post_id, flow))
            flowObject = ConversationFlow.objects.create(
                flow_name=compute_flow_name(flow, "sample_"),
                conversation_id=flow[0].tree_id,
                longest=False,
                sample_flow=timezone.now().date(),
                mt_study_flow=True
            )
            flowObject.tweets.set(Tweet.objects.filter(twitter_id__in=tweet_ids))
        except IntegrityError:
            dublicated_count += 1
    return dublicated_count


def is_short_text(text):
    """
    Check if the given text is shorter than 280 characters.

    Args:
        text (str): The text to be checked.

    Returns:
        bool: True if the text is shorter than 280 characters, False otherwise.
    """
    return len(text) < 500


def is_bad_reddit_case(text):
    return "[removed]" not in text and "!approve" not in text and "!ban" not in text


def meta_list_filter(posts: list[DelabPost]):
    return all([meta_filter(x) for x in posts]) and filter_self_answers(posts)


def meta_filter(post: DelabPost):
    text = post.text
    is_short = is_short_text(text)
    is_bad_rd = is_bad_reddit_case(text)
    result = is_short and is_bad_rd
    return result


def filter_self_answers(posts: list[DelabPost]):
    # posts = posts.sort(key=lambda x: x.created_at)
    previous_author = None
    for post in posts:
        if post.author_id == previous_author:
            return False
        previous_author = post.author_id
    return True
