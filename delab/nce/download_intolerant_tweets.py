import csv
import os
import time
from pathlib import Path

import yaml
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.utils import IntegrityError

from delab.corpus.download_conversations import download_conversations
from delab.models import LANGUAGE, Tweet, TWCandidateIntolerance
from delab.toxicity.perspectives import get_client
from util.abusing_lists import batch


def download_terrible_tweets(download_dictionary, link, download_right_wing=False):
    for lang in LANGUAGE:
        with open("delab/nce/bad_words.csv") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            # next(reader, None)  # skip the headers

            data_read = [row for row in reader if row[1] == lang]

            if download_dictionary:
                download_bad_tweets(data_read, lang)

            if download_right_wing:
                download_right_wing_toxic_tweets()

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


def mark_tweet_as_intolerant_candidate(tweet):
    tweet.save()
    TWCandidateIntolerance.objects.create(
        tweet=tweet
    )
    return tweet


def get_right_wing_tag_based_query():
    settings_dir = os.path.dirname(__file__)
    project_root = Path(os.path.dirname(settings_dir)).absolute()
    keys_path = os.path.join(project_root, '../twitter/nce/far_right_tweet_authors.yaml')
    with open(keys_path) as f:
        my_dict = yaml.safe_load(f)
        right_wing_german_tags = my_dict.get("de")
    return right_wing_german_tags


def download_right_wing_toxic_tweets():
    def conversation_filter(root_node):
        """
        This makes sure that only conversations with a general toxicity are returned
        :param root_node:
        :return:
        """
        toxic_sum, count = check_toxic_tree(root_node)
        # if the general toxicity level of the conversation is fine, we are not interested
        if toxic_sum / count < 0.5:
            return None
        else:
            return root_node

    def tweet_filter(tweet):
        """
        This marks highly toxic tweets as candidates to be labeled as intolerant
        :param tweet:
        :return:
        """
        if get_toxicity(tweet.text) > 0.9:
            # this is only a proxy other measures such as involvement of a group might be interesting
            return mark_tweet_as_intolerant_candidate(tweet)
        else:
            return tweet

    query = ""
    tags = get_right_wing_tag_based_query()
    for b in batch(tags, 10):
        for tag in b[:-1]:
            query += " from:" + tag + " OR "
        query += tags[-1]

        download_conversations("right_wing", query, conversation_filter=None, tweet_filter=tweet_filter,
                               language=LANGUAGE.GERMAN)
        break


def check_toxic_tree(parent):
    toxic_sum = get_toxicity(parent.data["text"])
    count = 1
    for child in parent.children:
        toxic_sum_children, count_children = check_toxic_tree(child)
        toxic_sum = toxic_sum + toxic_sum_children
        count = count_children + count

    return toxic_sum, count


def get_toxicity(text):
    toxicity = 0
    client = get_client()
    if len(text) > 1:
        try:
            analyze_request = {
                'comment': {
                    'text': text},
                'requestedAttributes': {'SEVERE_TOXICITY': {}}
            }
            response = client.comments().analyze(body=analyze_request).execute()
            toxicity = response["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
            time.sleep(2)
        except Exception:
            print("something went wrong")
    return toxicity
