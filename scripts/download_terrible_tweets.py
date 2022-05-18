from background_task.models import Task

from delab.tasks import download_intolerant_tweets


def run():
    download_intolerant_tweets(repeat=Task.DAILY)
