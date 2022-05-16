from delab.nce.download_intolerant_tweets import download_terrible_tweets


def run():
    download_terrible_tweets(False, True, download_right_wing=False)

