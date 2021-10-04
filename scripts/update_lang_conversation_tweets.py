from django.db.models import Q
from googletrans import Translator
from delab.models import Tweet


def run():
    tweets = Tweet.objects.filter(Q(language="unk")).all()
    translator = Translator()
    for tweet in tweets:
        detected = translator.detect(tweet.text)
        print("dectted lang {}".format(detected.lang))
        tweet.language = detected.lang
        tweet.save(update_fields=["language"])
