from background_task.models import Task

from delab.tasks import download_intolerant_tweets, download_moderating_tweets


def run():
    """
      This sets off the pipeline for downloading intolerant and moderating tweets.
      This triggers the daily cron-job in the django background framework

      :return:
      """
    # deleting previous daily cron jobs
    # background_tasks = start_intolerant_tweet_job()

    start_moderating_tweet_job()


def start_moderating_tweet_job():
    background_tasks = Task.objects.filter(task_name='delab.tasks.download_moderating_tweets')
    # deleting previous daily cron jobs
    for background_task in background_tasks:
        background_task.delete()
    # adding the new task to the stack
    download_moderating_tweets(repeat=Task.WEEKLY)


def start_intolerant_tweet_job():
    background_tasks = Task.objects.filter(task_name='delab.tasks.download_intolerant_tweets')
    for background_task in background_tasks:
        background_task.delete()
    # adding the new task to the stack
    download_intolerant_tweets(repeat=Task.WEEKLY)
    return background_tasks



