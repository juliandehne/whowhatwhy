from background_task.models import Task

from delab.tasks import download_intolerant_tweets


def run():
    """
    This sets off the pipeline for downloading intolerant tweets.
    This triggers the daily cron-job in the django background framework

    :return:
    """
    # deleting previous daily cron jobs
    background_tasks = Task.objects.filter(task_name='delab.tasks.download_intolerant_tweets')
    for background_task in background_tasks:
        background_task.delete()

    # adding the new task to the stack
    download_intolerant_tweets(repeat=Task.DAILY)
