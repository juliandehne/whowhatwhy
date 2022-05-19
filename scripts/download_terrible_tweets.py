from background_task.models import Task

from delab.tasks import download_intolerant_tweets


def run():
    """
    This sets off the pipeline for downloading intolerant tweets.
    This triggers the daily cron-job in the django background framework

    :return:
    """
    download_intolerant_tweets(repeat=Task.DAILY)
