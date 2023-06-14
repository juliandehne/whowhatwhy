from background_task.models import Task

from delab.nce.download_intolerant_tweets import download_terrible_tweets
from delab.tasks import download_intolerant_tweets


def run():
    download_terrible_tweets(True, True)
