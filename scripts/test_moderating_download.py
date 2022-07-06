from delab.mm.download_moderating_tweets import MODTOPIC2
from delab.models import Tweet


def run():
    conversation_ids = set(Tweet.objects.filter(topic__title=MODTOPIC2).values_list("conversation_id", flat=True).all())
    print(conversation_ids)
