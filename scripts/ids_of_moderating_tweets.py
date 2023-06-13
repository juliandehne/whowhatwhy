import pandas as pd

from delab.models import SimpleRequest, Tweet


def run():
    search_terms_de = ["bleib beim Thema", "näher erläutern", "entspann dich"]
    search_terms_en = ["back to topic", "back to the topic", "stick to topic", "can you elaborate"]
    search_terms = search_terms_de + search_terms_en
    sr_list = []
    for search_term in search_terms:
        srs = SimpleRequest.objects.filter(title__contains=search_term)
        for sr in srs:
            # print(sr.title)
            sr_list.append(sr)
    tweets = Tweet.objects.filter(simple_request__in=sr_list).all()
    df = pd.DataFrame(
        list(tweets.values('twitter_id', 'text', 'created_at', 'author_id', 'sentiment_value', 'conversation_id',
                           'language', 'tn_parent_id', 'platform', 'toxic_value')))
    df.to_pickle("mm_tweets_export.pkl")
