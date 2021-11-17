from django.db.models import Q

from delab.models import Tweet
from delab.analytics.moderator_dictionary import moderating_words


def run():
    query = Q()
    for word in moderating_words:
        query = query | Q(text__contains=word)
    results = Tweet.objects.filter(query)
    for result in results:
        print(result.text)

