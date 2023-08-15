from delab.corpus.reddit.download_conversations_reddit import download_subreddit
from delab.tw_connection_util import get_praw


def run():

    subreddit_list = [
        "incest",
        "Incestconfessions",
        "abortion",
        "addiction",
        "Drugs",
        "STD",
        "erectiledysfunction"
    ]
    praw = get_praw()
    # qurantine =
    for i in subreddit_list:
        download_subreddit(i)
