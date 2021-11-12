import logging

from background_task import background

from delab.corpus.download_author_information import update_authors
from delab.corpus.download_conversations import download_conversations
from delab.models import Tweet
from django.db.models import Q
from background_task.models import Task
from background_task.models import CompletedTask
from django.utils import timezone


logger = logging.getLogger(__name__)


@background(schedule=1)
def download_conversations_scheduler(topic_string, hashtags, simple_request_id, simulate=True,
                                     max_data=False,
                                     fast_mode=False):
    if simulate:
        logger.error("pretending to downloading conversations{}".format(hashtags))
    else:
        download_conversations(topic_string, hashtags, simple_request_id, max_data=max_data, fast_mode=fast_mode)
        if fast_mode:
            update_sentiments(simple_request_id,
                              verbose_name="sentiment_analysis_{}".format(simple_request_id),
                              schedule=timezone.now())
        else:
            update_author(simple_request_id,
                          verbose_name="author_analysis_{}".format(simple_request_id),
                          schedule=timezone.now())


@background(schedule=1)
def update_author(simple_request_id=-1):
    update_authors(simple_request_id)
    update_author_timelines(simple_request_id, verbose_name="timeline_download_{}".format(simple_request_id),
                            schedule=timezone.now())


@background(schedule=1)
def update_sentiments(simple_request_id=-1):
    from delab.sentiment.sentiment_classification import update_tweet_sentiments

    update_tweet_sentiments(simple_request_id)
    update_flows(simple_request_id=simple_request_id, verbose_name="flow_analysis_{}".format(simple_request_id),
                 schedule=timezone.now())


@background(schedule=1)
def update_flows(simple_request_id=-1):
    from delab.sentiment.sentiment_flow_analysis import update_sentiment_flows
    update_sentiment_flows(simple_request_id)


@background(schedule=1)
def update_author_timelines(simple_request_id=-1):
    from delab.topic.topic_data_preperation import update_timelines_from_conversation_users
    from django_project.settings import TRAX_CAPABILITIES

    update_timelines_from_conversation_users(simple_request_id)
    if TRAX_CAPABILITIES:
        update_sentiments(simple_request_id,
                          verbose_name="sentiment_analysis_{}".format(simple_request_id),
                          schedule=timezone.now())


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
