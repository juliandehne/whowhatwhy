from django.db.models import Q
from googletrans import Translator
from delab.models import Tweet
from django.db.models import Count

from delab.models import SimpleRequest


def run():
    simple_request = SimpleRequest.objects.filter(id=39).get()
    result = Tweet.objects.filter(Q(simple_request=simple_request) & Q(tn_parent_id__isnull=True))
    print(len(result))


def runzz():
    dups = (
        Tweet.objects.values('text')
            .annotate(count=Count('id'))
            .values('text')
            .order_by()
            .filter(count__gt=1)
    )
    print(dups)
    for elem in dups:
        to_delete_text = elem.get("text")
        Tweet.objects.filter(text=to_delete_text).delete()

    # print(len(dups))


def runz():
    tweets = Tweet.objects.filter(Q(language="unk")).all()
    translator = Translator()
    for tweet in tweets:
        detected = translator.detect(tweet.text)
        print("dectted lang {}".format(detected.lang))
        tweet.language = detected.lang
        tweet.save(update_fields=["language"])
