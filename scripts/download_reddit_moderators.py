from delab.tw_connection_util import get_praw
from delab.corpus.download_timelines_reddit import download_timelines


def run():
    #    download_timelines()
    reddit = get_praw()

    subreddit = reddit.subreddit("COVID19")
    for moderator in subreddit.moderator():
        print(moderator)
