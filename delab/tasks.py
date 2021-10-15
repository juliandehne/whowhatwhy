import logging

from background_task import background

from delab.corpus.download_conversations import download_conversations
from delab.models import Tweet
from django.db.models import Q
from background_task.models import Task
from background_task.models_completed import CompletedTask
from django.utils import timezone

logger = logging.getLogger(__name__)


@background(schedule=1)
def download_conversations_scheduler(topic_string, hashtags, simple_request_id, simulate=True, max_data=False):
    if simulate:
        logger.error("pretending to downloading conversations{}".format(hashtags))
    else:
        download_conversations(topic_string, hashtags, simple_request_id, max_data=max_data)
        # update_sentiments()
        # update_sentiment_flows()


def update_sentiments():
    from delab.sentiment.sentiment_classification import classify_tweet_sentiment
    logger.info("updating sentiments")
    # importing here to improve server startup time

    tweets = Tweet.objects.filter((Q(sentiment=None) | Q(sentiment_value=None)) & ~Q(sentiment="failed_analysis")).all()
    # tweet_strings = tweets.values_list(["text"], flat=True)
    # print(tweet_strings[1:3])
    tweet_strings = list(map(lambda x: x.text, tweets))
    predictions, sentiments, sentiment_values = classify_tweet_sentiment(tweet_strings)
    for tweet in tweets:
        tweet.sentiment = sentiments.get(tweet.text, "failed_analysis")
        tweet.sentiment_value = sentiment_values.get(tweet.text, None)
        tweet.save()


def get_tasks_status():
    now = timezone.now()

    # pending tasks will have `run_at` column greater than current time.
    # Similar for running tasks, it shall be
    # greater than or equal to `locked_at` column.
    # Running tasks won't work with SQLite DB,
    # because of concurrency issues in SQLite.
    pending_tasks_qs = Task.objects.filter(run_at__gt=now).all()
    running_tasks_qs = Task.objects.filter(locked_at__gte=now).all()

    # Completed tasks goes in `CompletedTask` model.
    # I have picked all, you can choose to filter based on what you want.
    completed_tasks_qs = CompletedTask.objects.all()

    # main logic here to return this as a response.

    # just for test
    print(pending_tasks_qs, running_tasks_qs, completed_tasks_qs)
    return pending_tasks_qs, running_tasks_qs, completed_tasks_qs


@background(schedule=1)
def start_first_task():
    print("started_first_task")
    start_second_task(verbose_name="second_tasks",
                      schedule=timezone.now())


@background(schedule=1)
def start_second_task():
    print("started_second_task")
