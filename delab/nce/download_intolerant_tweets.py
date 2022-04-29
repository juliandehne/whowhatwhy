import csv

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.utils import IntegrityError

from delab.corpus.download_conversations import download_conversations
from delab.models import LANGUAGE, Tweet, TWCandidateIntolerance


def download_terrible_tweets(download, link):
    for lang in LANGUAGE:
        with open("delab/nce/bad_words.csv") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            # next(reader, None)  # skip the headers

            data_read = [row for row in reader if row[1] == lang]

            if download:
                download_bad_tweets(data_read, lang)

            if link:
                find_and_link_bad_tweets(data_read, lang)


def find_and_link_bad_tweets(data_read, lang):
    """
    This relies on postgres language based search. However, this only supports certain languages:
    simple
     arabic
     armenian
     basque
     catalan
     danish
     dutch
     english
     finnish
     french
     german
     greek
     hindi
     hungarian
     indonesian
     irish
     italian
     lithuanian
     nepali
     norwegian
     portuguese
     romanian
     russian
     serbian
     spanish
     swedish
     tamil
     turkish
     yiddish

     Note that polish is not included!

    :return:
    """

    word2category = {}
    word2goodword = {}
    for row in data_read:
        word2category[row[0]] = row[2]
        word2goodword[row[0]] = row[3]

    if len(data_read) > 5:
        query = "('" + data_read[0][0] + "'" + " | "
        for row in data_read[1:-2]:
            query += "'" + row[0] + "'" + " | "
        query += "'" + data_read[-1][0] + "'" + ")"
        search_query = SearchQuery(query, search_type="raw")

        vector = SearchVector('text')
        if lang == LANGUAGE.ENGLISH:
            vector = SearchVector('text', config='english')
        if lang == LANGUAGE.GERMAN:
            vector = SearchVector('text', config='german')
        if lang == LANGUAGE.SPANISH:
            vector = SearchVector('text', config='spanish')

        found_tweets = Tweet.objects.filter(twcandidateintolerance=None) \
            .filter(language=lang) \
            .annotate(search=vector) \
            .filter(search=search_query)

        not_filtered = found_tweets.all()
        for word in word2category.keys():
            found_tweets = found_tweets.exclude(text__iregex=r'@[^\ ]*' + word + '')
            found_tweets = found_tweets.exclude(text__iregex=r'#[^\ ]*' + word + '')
            found_tweets = found_tweets.exclude(text__iregex=r'"[^\ ]*' + word + '')
            found_tweets = found_tweets.exclude(text__iregex=r'„[^\ ]*' + word + '')

        # found_tweets = found_tweets.all()
        # apply_new_filters(found_tweets, not_filtered)

        for tweet in found_tweets:
            for word in word2category.keys():
                if word in tweet.text:
                    if not TWCandidateIntolerance.objects.filter(tweet_id=tweet.id).exists():
                        TWCandidateIntolerance.objects.create(
                            first_bad_word=word,
                            tweet=tweet,
                            dict_category=word2category[word],
                            political_correct_word=word2goodword[word]
                        )


def apply_new_filters(found_tweets, not_filtered):
    for tweet in not_filtered:
        if tweet not in found_tweets:
            try:
                TWCandidateIntolerance.objects.filter(tweet_id=tweet.id).delete()
            except IntegrityError:
                pass


def download_bad_tweets(data_read, lang):
    if len(data_read) > 5:
        query = data_read[0][0] + " OR "
        for row in data_read[1:-2]:
            query += row[0] + " OR "
        query += data_read[-1][0]
        # print(query)
        download_conversations(topic_string="intolerance_dict", query_string=query, request_id=-1,
                               language=lang)
