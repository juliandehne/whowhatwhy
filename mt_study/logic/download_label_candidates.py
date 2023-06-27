import pickle
import timeit

from delab.corpus.download_conversations_proxy import download_daily_sample

from delab.delab_enums import PLATFORM

M_TURK_TOPIC = "mturk_candidate"


def download_mturk_sample_conversations(n_runs):
    # Perform 100 runs of the function and measure the time taken
    execution_time = timeit.timeit(download_mturk_samples, number=n_runs)
    average_time = (execution_time / 100) / 60
    print("Execution time:", execution_time, "seconds")
    print("Aberage Execution time:", average_time, "minutes")


def download_mturk_samples():
    result = []
    print("down""loading random conversations for mturk_labeling")
    exception_counter = 0
    while len(result) < 20:
        try:
            downloaded_trees = download_daily_sample(topic_string=M_TURK_TOPIC, platform=PLATFORM.TWITTER)
            for tree in downloaded_trees:
                tree.validate(verbose=False)
            result += downloaded_trees
            print("downloaded candidates:", len(result))
        except Exception as ex:
            print(ex)
            exception_counter += 1
            if exception_counter > 100:
                break
    with open('todays_trees.pkl', 'wb') as file:
        pickle.dump(result, file)
        file.close()
