from delab.tw_connection_util import get_praw
from delab.corpus.download_timelines_reddit import download_timelines


def run():
    #    download_timelines()
    reddit = get_praw()

    for moderator in reddit.subreddit("redditdev").moderator():
        print(f"{moderator}: {moderator.mod_permissions}")
