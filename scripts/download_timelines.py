from delab.corpus.download_timelines_reddit import download_timelines_reddit
from delab.corpus.download_timelines_twitter import update_timelines_twitter


def run():
    update_timelines_twitter(fix_legacy_db=True)
    download_timelines_reddit()
