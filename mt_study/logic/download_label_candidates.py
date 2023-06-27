import pickle
import timeit
from functools import partial

from delab.corpus.download_conversations_proxy import download_daily_sample

from delab.delab_enums import PLATFORM
from delab_trees.delab_tree import DelabTree

M_TURK_TOPIC = "mturk_candidate"


def download_mturk_sample_conversations(n_runs, platform):
    # Perform 100 runs of the function and measure the time taken

    download_mturk_sample_helper = partial(download_mturk_samples, platform)
    execution_time = timeit.timeit(download_mturk_sample_helper, number=n_runs)
    average_time = (execution_time / 100) / 60
    print("Execution time:", execution_time, "seconds")
    print("Aberage Execution time:", average_time, "minutes")


def download_mturk_samples(platform=PLATFORM.TWITTER) -> list[DelabTree]:
    result = []
    print("down""loading random conversations for mturk_labeling")
    exception_counter = 0
    while len(result) < 20:
        # try:
        downloaded_trees = download_daily_sample(topic_string=M_TURK_TOPIC, platform=platform)
        for tree in downloaded_trees:
            tree.validate(verbose=False)
        result += downloaded_trees
        print("downloaded candidates:", len(result))
        """
        except Exception as ex:
            print(ex)
            exception_counter += 1
            if exception_counter > 100:
                break
        """
    with open('todays_trees.pkl', 'wb') as file:
        pickle.dump(result, file)
        file.close()
