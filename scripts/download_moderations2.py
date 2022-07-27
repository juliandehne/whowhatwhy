from delab.delab_enums import PLATFORM
from delab.mm.download_moderating_tweets import download_mod_tweets


def run():
    # download_mod_tweets(recent=True, platform=PLATFORM.TWITTER)
    download_mod_tweets(recent=True, platform=PLATFORM.REDDIT)
