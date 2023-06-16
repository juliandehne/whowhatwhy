from delab.corpus.download_conversations_proxy import download_daily_sample

from delab.delab_enums import PLATFORM

M_TURK_TOPIC = "mturk_candidate"


def download_mturk_sample_conversations():
    print("downloading random conversations for mturk_labeling")
    downloaded_trees = download_daily_sample(topic_string=M_TURK_TOPIC, platform=PLATFORM.TWITTER)
    for tree in downloaded_trees:
        tree.validate(verbose=False)
    print("downloaded candidates")
