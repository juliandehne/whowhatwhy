from delab.delab_enums import PLATFORM
from mt_study.logic.download_label_candidates import download_mturk_sample_conversations


def run():
    download_mturk_sample_conversations(1, platform=PLATFORM.MASTODON, min_results=20)
