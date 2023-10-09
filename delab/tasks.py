import logging
from functools import partial

from background_task import background
from background_task.models import CompletedTask
from background_task.models import Task
from django.utils import timezone
from delab.corpus.twitter.download_author_information import update_authors
from delab.corpus.download_conversations_proxy import download_conversations, download_timelines
from mt_study.logic.download_label_candidates import download_mturk_sample_conversations
from .delab_enums import PLATFORM, LANGUAGE
from .mm.download_moderating_tweets import download_mod_tweets, MODTOPIC2, tweet_filter_helper, MODTOPIC2_WEBSITE
from .nce.download_intolerant_tweets import download_terrible_tweets
from .network.conversation_network import download_twitter_follower
from .sentiment.sentiment_classification import update_tweet_sentiments
from .toxicity.perspectives import compute_toxicity_for_text
from django_project.settings import MT_STUDY_DAILY_FLOWS_NEEDED, MT_STUDY_DAILY_FLOWS_NEEDED_DE

logger = logging.getLogger(__name__)


@background(schedule=1)
def download_conversations_scheduler(topic_string, platform, query_string, simple_request_id, simulate=True,
                                     max_data=False,
                                     fast_mode=False, language=LANGUAGE.ENGLISH):
    moderation_tweet_filter = partial(tweet_filter_helper, query_string, simple_request_id)

    if simulate:
        logger.error("pretending to downloading conversations{}".format(query_string))
    else:
        download_param_dict = {"topic_string": topic_string,
                               "query_string": query_string,
                               "request_id": simple_request_id,
                               "language": language,
                               "max_data": max_data,
                               "platform": platform,
                               "fast_mode": fast_mode,
                               "recent": False
                               }
        if topic_string == MODTOPIC2_WEBSITE:
            download_param_dict["topic_string"] = MODTOPIC2
            if platform == PLATFORM.TWITTER:
                download_conversations(**download_param_dict,
                                       tweet_filter=moderation_tweet_filter)
            if platform == PLATFORM.REDDIT:
                download_conversations(**download_param_dict,
                                       tweet_filter=moderation_tweet_filter)
        else:
            if platform == PLATFORM.TWITTER:
                download_conversations(**download_param_dict)
            if platform == PLATFORM.REDDIT:
                download_conversations(**download_param_dict)

        update_author(simple_request_id, platform, fast_mode, language,
                      verbose_name="author_analysis_{}".format(simple_request_id),
                      schedule=timezone.now())


@background(schedule=1)
def update_author(simple_request_id=-1, platform=PLATFORM.TWITTER, fast_mode=False, language=LANGUAGE.ENGLISH):
    if not fast_mode:
        update_authors(simple_request_id, platform=platform)
        update_author_timelines(simple_request_id, platform, language,
                                verbose_name="timeline_download_{}".format(simple_request_id),
                                schedule=timezone.now())


@background(schedule=1)
def update_author_timelines(simple_request_id=-1, platform=PLATFORM.TWITTER, language=LANGUAGE.ENGLISH):
    download_timelines(simple_request_id, platform=platform)
    update_sentiments(simple_request_id, language,
                      verbose_name="sentiment_analysis_{}".format(simple_request_id),
                      schedule=timezone.now())


@background(schedule=1)
def update_sentiments(simple_request_id=-1, language=LANGUAGE.ENGLISH):
    update_tweet_sentiments(simple_request_id, language)
    update_flows(simple_request_id=simple_request_id, verbose_name="flow_analysis_{}".format(simple_request_id),
                 schedule=timezone.now())


@background(schedule=1)
def update_flows(simple_request_id=-1):
    from .analytics.flow_picture_computation import update_flow_picture
    update_flow_picture(simple_request_id)


def get_tasks_status(simple_request_id):
    now = timezone.now()

    # pending tasks will have `run_at` column greater than current time.
    # Similar for running tasks, it shall be
    # greater than or equal to `locked_at` column.
    # Running tasks won't work with SQLite DB,
    # because of concurrency issues in SQLite.
    # pending_tasks_qs = Task.objects.filter(run_at__gt=now).all()
    # running_tasks_qs = Task.objects.filter(locked_at__gte=now).all()
    running_tasks_qs = Task.objects.filter(verbose_name__contains=simple_request_id).all()

    # Completed tasks goes in `CompletedTask` model.
    # I have picked all, you can choose to filter based on what you want.
    completed_tasks_qs = CompletedTask.objects.all()

    # main logic here to return this as a response.

    # just for test
    # print(pending_tasks_qs, running_tasks_qs, completed_tasks_qs)
    # return pending_tasks_qs, running_tasks_qs, completed_tasks_qs
    return running_tasks_qs


@background()
def download_intolerant_tweets():
    logger.debug("CRONJOB: downloading intolerant tweets")
    download_terrible_tweets(True, True)


@background()
def download_moderating_tweets():
    logger.debug("CRONJOB: downloading moderating tweets")
    download_mod_tweets(recent=True)


@background()
def download_network_structures():
    logger.debug("CRONJOB: downloading networks!")
    levels = 1
    n_conversations = -1
    download_twitter_follower(levels, n_conversations)


@background()
def update_toxic_values():
    logger.debug("CRONJOB: update toxic networks!")
    compute_toxicity_for_text()


@background()
def download_daily_sample():
    logger.debug("CRONJOB: downloading_daily_sample flow!")

    download_mturk_sample_conversations(n_runs=1,
                                        platform=PLATFORM.MASTODON,
                                        min_results=MT_STUDY_DAILY_FLOWS_NEEDED,
                                        language=LANGUAGE.ENGLISH)
    download_mturk_sample_conversations(n_runs=1,
                                        platform=PLATFORM.MASTODON,
                                        min_results=MT_STUDY_DAILY_FLOWS_NEEDED_DE,
                                        language=LANGUAGE.GERMAN)

    download_mturk_sample_conversations(n_runs=1,
                                        platform=PLATFORM.REDDIT,
                                        min_results=MT_STUDY_DAILY_FLOWS_NEEDED,
                                        language=LANGUAGE.ENGLISH)
    download_mturk_sample_conversations(n_runs=1,
                                        platform=PLATFORM.REDDIT,
                                        min_results=MT_STUDY_DAILY_FLOWS_NEEDED_DE,
                                        language=LANGUAGE.GERMAN)
