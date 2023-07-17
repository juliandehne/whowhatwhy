from delab.delab_enums import PLATFORM
from django_project.settings import MT_STUDY_DAILY_FLOWS_NEEDED
from mt_study.logic.download_label_candidates import download_mturk_sample_conversations


def run():
    download_mturk_sample_conversations(1, platform=PLATFORM.REDDIT, min_results=MT_STUDY_DAILY_FLOWS_NEEDED)
