from delab.delab_enums import PLATFORM, LANGUAGE
from django_project.settings import MT_STUDY_DAILY_FLOWS_NEEDED, MT_STUDY_DAILY_FLOWS_NEEDED_DE
from mt_study.logic.download_label_candidates import download_mturk_sample_conversations


def run():

    download_mturk_sample_conversations(n_runs=1,
                                        platform=PLATFORM.MASTODON,
                                        min_results=100,
                                        language=LANGUAGE.ENGLISH)

    download_mturk_sample_conversations(n_runs=1,
                                        platform=PLATFORM.MASTODON,
                                        min_results=100,
                                        language=LANGUAGE.GERMAN)

    """
    download_mturk_sample_conversations(n_runs=1,
                                        platform=PLATFORM.REDDIT,
                                        min_results=MT_STUDY_DAILY_FLOWS_NEEDED_DE,
                                        language=LANGUAGE.GERMAN)
    """