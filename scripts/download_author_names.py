from delab.corpus.download_author_information import update_authors
from delab.models import Tweet


def run():
    topic = "freespech"

    result = Tweet.objects.filter(tw_author__isnull=True, topic__title=topic).all()

    update_authors()
    # update_authors()
