import html
import json
import logging
import os
import random
import re
from pathlib import Path

import fasttext.util
import numpy as np
from bertopic import BERTopic
from django.contrib.postgres.aggregates import StringAgg
from django.db import IntegrityError
from django.db.models import Q
from django_pandas.io import read_frame

from delab.delab_enums import PLATFORM, LANGUAGE
from delab.models import Timeline, Tweet, TweetAuthor
from delab.models import TopicDictionary
from delab.topic.topic_exceptions import BertopicModelMissingException
from delab.topic.topic_settings import get_embedding_model, get_bertopic_location
from util import TVocabulary
from util.abusing_lists import batch

logger = logging.getLogger(__name__)

"""
1. Create a seperate file and run the bert_topic fitting there, call this function with train = True for testing
    a) run the fitting [x]
    b) use the bert_topic transform to get all the the topic words [x]
    c) get embedding vectors from fasttest using the topic words [x]
    d) store the embeddings vectors in database [x]
    e) store the bert_topic model [x]

"""


def train_topic_model_from_db(version, train=True, platform=PLATFORM.TWITTER, language=LANGUAGE.ENGLISH,
                              store_vectors=True,
                              number_of_batches=30000, topic=None):
    """
    :param topic:
    :param version: creates different trained bertopic models for the version tag
    :param train: boolean (retrain or use existing trained model)
    :param platform: 
    :param language:
    :param store_vectors: Stores the embedding vectors from fasttext in a table for quick access for each word in the tweets
    :param number_of_batches: The number of tweets used for training the model (should be the all of them if there is time)
    :return:
    """
    logger.debug("starting to train the topic model")
    corpus_for_fitting_sentences = get_train_corpus_for_sentences(version, language, platform,
                                                                  max_size=number_of_batches, topic=topic)

    if len(corpus_for_fitting_sentences) < 10:
        logger.info("not enough data found to train model")
    else:
        if train:
            train_bert(corpus_for_fitting_sentences, language, version, topic)

        if store_vectors:
            vocab = create_vocabulary(corpus_for_fitting_sentences)
            store_embedding_vectors(vocab, language, version, topic)

        logger.debug("finished training the topic model")


def train_bert(corpus_for_fitting_sentences, language, version, topic=None):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    # for trainings_batch in batch(corpus_for_fitting_sentences, 1000):
    trainings_batch = corpus_for_fitting_sentences

    embedding_model = get_embedding_model(language)

    # bertopic_model = BERTopic(embedding_model=embedding_model, verbose=True,
    #                          calculate_probabilities=False, min_topic_size=30, low_memory=True)

    bertopic_model = BERTopic(embedding_model=embedding_model, verbose=True,
                              calculate_probabilities=False)

    bertopic_model.fit_transform(trainings_batch)
    location = get_bertopic_location(language, version, topic)
    bertopic_model.save(location)
    logger.debug("saved trained model to location {}".format(location))


def filter_bad_topics(bertopic_model, vocab):
    bad_topics = get_bad_topics(vocab, bertopic_model)
    topic_info = bertopic_model.get_topic_info()
    # topic_info["Topic"]
    mask = topic_info["Topic"].isin(bad_topics)
    mask = mask[mask == True]
    topic_info.drop(index=mask.index, inplace=True)
    return topic_info


def store_embedding_vectors(vocab, lang, version, topic=None):
    """
    This calculates the words that are in the topics, finds fasttext vectors for these words
    and stores them in the database for the distance measuring later on.
    :param vocab:
    :param lang:
    :return:
    """

    # fasttext.util.download_model('en', if_exists='ignore')  # English
    fasttext.util.download_model('en', if_exists='ignore')
    fasttext.util.download_model('de', if_exists='ignore')

    if lang == LANGUAGE.ENGLISH:
        ft = fasttext.load_model('cc.en.300.bin')
    if lang == LANGUAGE.GERMAN:
        ft = fasttext.load_model('cc.de.300.bin')
    logger.debug("loaded fasttext model into memory")
    # dim = ft.get_dimension()
    location = get_bertopic_location(lang, version, topic)
    embedding_model = get_embedding_model(lang)
    bertopic_model = BERTopic.load(location, embedding_model=embedding_model)
    logger.debug("loaded berttopic model")

    # filter topics
    # topic_info = filter_bad_topics(bertopic_model, vocab)
    topic_info = bertopic_model.get_topic_info()

    n_words_nin_voc = 0
    n_words_in_voc = 0
    for topic_id in topic_info.Topic:
        topic_model = bertopic_model.get_topic(topic_id)
        for t_word in topic_model:
            str_w = t_word[0]
            if str_w not in ft.words:
                n_words_nin_voc += 1
            else:
                n_words_in_voc += 1
                ft_vector = ft.get_word_vector(str_w)
                try:
                    TopicDictionary.objects.get_or_create(word=str_w, ft_vector=json.dumps(ft_vector, cls=NumpyEncoder))
                except IntegrityError:
                    logger.debug("trying to save existing vector for word {} to db".format(str_w))
    print("saved ft_vectors. The hit rate was: {}".format(n_words_in_voc / (n_words_in_voc + n_words_nin_voc)))
    bertopic_model = None  # for the gc


def get_bad_topics(vocab, topic_model_2):
    """
    Tests if the words in the topic are actual words in the vocabulary
    :param vocab: the vocabulary created from allt he tweets in the database
    :param topic_model_2: the topic model trained on the tweets
    :return:
    """
    topic_info = topic_model_2.get_topic_info()
    topic_info_no_outlier = topic_info.drop(index=0)

    topic_quality = {}
    # topic_info.drop(index=[0], inplace=True)  # dropping the undefined topic
    for topic_id in topic_info_no_outlier.Topic:
        topic_model = topic_model_2.get_topic(topic_id)
        number_example_words = len(topic_model)
        # print(number_example_words)
        missing_words = 0
        # print(topic_model)
        for t_word in topic_model:
            str_w = t_word[0]
            # print(str_w)
            if not vocab.is_in(str_w):
                # print(str_w)
                missing_words += 1
        topic_quality[topic_id] = (number_example_words - missing_words) / number_example_words
    bad_topics = []
    for topic_id, quality_value in topic_quality.items():
        if quality_value <= 0.7:
            bad_topics.append(topic_id)

    bad_topics.append(-1)
    return bad_topics


def get_train_corpus_for_sentences(version, lang, platform, max_size=-1, topic=None):
    """
    This constructs the training corpus for the topic analysis.
    :param topic:
    :param platform:
    :param lang:
    :param max_size: in order to improve testing, it is possible to set max_size > 0 to just train on a subset of the data
    :return: list[str] a list of tweets
    """
    # author_tweets_texts, logger = load_author_tweets(version, lang, platform)
    conversation_tweets_texts = load_conversation_tweets(version, lang, platform, topic)
    # corpus_for_fitting_sentences = create_tweet_corpus_for_bertopic(author_tweets_texts, conversation_tweets_texts)

    corpus_for_fitting_sentences = clean_corpus(conversation_tweets_texts)

    if max_size < 0:
        return corpus_for_fitting_sentences
    if len(corpus_for_fitting_sentences) < max_size:
        logger.error(
            "there are only {} sentences available in the db to analyse the topics".format(
                len(corpus_for_fitting_sentences)))
        return corpus_for_fitting_sentences
    corpus = random.sample(corpus_for_fitting_sentences, max_size)
    return corpus


def seperate_sentences_manually(text):
    # -*- coding: utf-8 -*-
    import re
    alphabets = "([A-Za-zÄÖÜäöü0-9])"
    prefixes = "(Mr|St|Mrs|Ms|Dr|Prof)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"

    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
    if "”" in text: text = text.replace(".”", "”.")
    if "\"" in text: text = text.replace(".\"", "\".")
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


def create_tweet_corpus_for_bertopic(author_tweets_texts, conversation_tweets_texts):
    """
    This flattens the tweets to a big set of sentences for the topic training.
    :param author_tweets_texts:
    :param conversation_tweets_texts:
    :return: list[str] a list of sentences for training
    """
    corpus_for_fitting = author_tweets_texts + conversation_tweets_texts
    # corpus_for_fitting = author_tweets_texts
    corpus_for_fitting_sentences = []
    for tweet in corpus_for_fitting:
        for sentence in tweet.split("."):
            corpus_for_fitting_sentences.append(sentence)
    corpus_for_fitting_sentences = clean_corpus(corpus_for_fitting_sentences)
    return corpus_for_fitting_sentences


def clean_corpus(corpus_for_fitting_sentences):
    """
    This is typical preprocessing in order to improve on the outcome of the topic analysis
    :param corpus_for_fitting_sentences:
    :return:
    """
    result = []
    for temp in corpus_for_fitting_sentences:
        original = temp
        # removing hashtags
        temp = re.sub(r"@[A-Za-z0-9äöüÄÖÜ_]+", "", temp)
        temp = re.sub(r"#[A-Za-z0-9äöüÄÖÜ_]+", "", temp)
        # removing links
        # if "https " in temp:
        #    print(temp)
        temp = re.sub(r"http\S+", "", temp)
        temp = re.sub(r"https\S+", "", temp)
        temp = re.sub(r"www.\S+", "", temp)
        # removing punctuation
        # temp = re.sub('[()!?]', ' ', temp)
        # temp = re.sub("\[.*?\]", ' ', temp)
        # alphanumeric
        # temp = re.sub("[^a-z0-9A-ZaäöüÄÖÜ]", "", temp)
        temp = re.sub("RT", "", temp)
        temp = re.sub("\n", "", temp)
        temp = html.unescape(temp)
        temp = temp.strip()
        temp = remove_emojis(temp)
        temp = re.sub(' +', ' ', temp)
        temp = re.sub("\.\.\.", " ldots ", temp)

        tweet_sentences = seperate_sentences_manually(temp + ".")
        cleaned_sentences = clean_sentences(tweet_sentences)
        result += cleaned_sentences

    return corpus_for_fitting_sentences


def clean_sentences(sentences):
    """
    This is typical preprocessing in order to improve on the outcome of the topic analysis
    :param corpus_for_fitting_sentences:
    :return:
    """
    result = []
    for temp in sentences:
        original = temp
        # removing hashtags

        # alphanumeric
        temp = re.sub("[^a-z0-9A-ZaäöüÄÖÜ\ \(\)\-\"\,\/]", "", temp)
        temp = re.sub("\(", " (", temp)
        temp = re.sub("\)", ") ", temp)
        number_of_words = len(temp.split(" ")) > 3
        if len(temp) > 1 and number_of_words:
            result.append(temp)
    return result


def remove_emojis(data):
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)


def classify_tweet_topics(version, language, platform=PLATFORM.TWITTER, update_topics=True, topic=None):
    try:
        location = get_bertopic_location(language, version, topic)
        embedding_model = get_embedding_model(language)
        bertopic_model = BERTopic.load(location, embedding_model=embedding_model)
        logger.debug("loaded berttopic model for classifying the tweets")

        # corpus_for_fitting_sentences = get_train_corpus_for_sentences(version, language, platform)
        # vocab = create_vocabulary(corpus_for_fitting_sentences)
        # load tweets
        # topic_info = filter_bad_topics(bertopic_model, vocab)
        topic_info = bertopic_model.get_topic_info()
        if update_topics:
            if topic is not None:
                conversation_tweets = Tweet.objects.filter(
                    Q(language=language) & Q(platform=platform) & Q(simple_request__version=version) & Q(
                        topic__title=topic))
            else:
                conversation_tweets = Tweet.objects.filter(
                    Q(language=language) & Q(platform=platform) & Q(simple_request__version=version))
        else:
            if topic is not None:
                conversation_tweets = Tweet.objects.filter(
                    Q(language=language) & Q(bertopic_id__isnull=True) & Q(platform=platform) & Q(
                        simple_request__version=version) & Q(topic__title=topic))
            else:
                conversation_tweets = Tweet.objects.filter(
                    Q(language=language) & Q(bertopic_id__isnull=True) & Q(platform=platform) & Q(
                        simple_request__version=version))

        if len(conversation_tweets) > 0:
            conversation_texts = list(conversation_tweets.values_list("text", flat=True))
            conversation_texts_cleaned = clean_corpus(conversation_texts)
            assert len(conversation_texts_cleaned) == len(conversation_texts)
            logger.debug("classifying the tweet topics...")
            suggested_topics = bertopic_model.transform(conversation_texts)
            suggested_topics = suggested_topics[0]
            index = 0
            conversation_tweet_objs = conversation_tweets.all()
            for conversation_tweet in conversation_tweet_objs:
                if suggested_topics[index] in topic_info.Topic:
                    if topic is not None:
                        conversation_tweet.topic_bertopic_id = suggested_topics[index]
                        topic_model = bertopic_model.get_topic(conversation_tweet.topic_bertopic_id)
                        visual_model = "{}".format(conversation_tweet.topic_bertopic_id)
                    else:
                        conversation_tweet.bertopic_id = suggested_topics[index]
                        topic_model = bertopic_model.get_topic(conversation_tweet.bertopic_id)
                        visual_model = "{}".format(conversation_tweet.bertopic_id)
                    for t_word in topic_model:
                        str_w = t_word[0]
                        visual_model += "_" + str_w
                        if topic is not None:
                            conversation_tweet.topic_bert_visual = visual_model
                        else:
                            conversation_tweet.bert_visual = visual_model
                else:
                    if topic is not None:
                        conversation_tweet.topic_bertopic_id = -2
                    else:
                        conversation_tweet.bertopic_id = -2
                index += 1
            if topic is not None:
                Tweet.objects.bulk_update(conversation_tweet_objs, ["topic_bertopic_id", "topic_bert_visual"])
            else:
                Tweet.objects.bulk_update(conversation_tweet_objs, ["bertopic_id", "bert_visual"])
        return bertopic_model
    except FileNotFoundError:
        logger.error("could not find model file for language {} and topic {}".format(language, topic))


def load_conversation_tweets(version, lang, platform, topic=None):
    if topic is not None:
        conversation_tweets = Tweet.objects.filter(
            Q(language=lang) & Q(simple_request__version=version) & Q(platform=platform) & Q(topic__title=topic)).all()
    else:
        conversation_tweets = Tweet.objects.filter(
            Q(language=lang) & Q(simple_request__version=version) & Q(platform=platform)).all()
    conversation_tweets_texts = list(conversation_tweets.values_list("text", flat=True))
    return conversation_tweets_texts


def load_author_tweets(version, lang, platform):
    tweets = Timeline.objects.filter(Q(lang=lang) & Q(platform=platform)).all()
    df = read_frame(tweets, fieldnames=["id",
                                        "author_id",
                                        "text",
                                        "conversation_id",
                                        "created_at",
                                        ])
    logger.info("loaded the timeline from the database")
    author_tweets_texts = list(df.text)
    return author_tweets_texts, logger


def create_vocabulary(corpus_for_fitting_sentences):
    vocab = TVocabulary()
    for corpus_for_fitting_sentence in corpus_for_fitting_sentences:
        vocab.add_sentence(corpus_for_fitting_sentence)
    return vocab


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def classify_author_timelines(version, language, update=True, platform=PLATFORM.TWITTER):
    location = get_bertopic_location(language, version)
    embedding_model = get_embedding_model(language)

    bertopic_model_path = Path(location)
    if not bertopic_model_path.is_file():
        raise BertopicModelMissingException(location, "timelines", language, version)

    bertopic_model = BERTopic.load(location, embedding_model=embedding_model)
    topic_info = bertopic_model.get_topic_info()
    logger.debug("loaded berttopic model")
    if update:
        tweet_authors = TweetAuthor.objects.prefetch_related('timeline_set').filter(
            has_timeline=True, platform=platform).filter(
            timeline__lang=language).annotate(
            timeline_text=StringAgg('timeline__text', delimiter='.'))
    else:
        tweet_authors = TweetAuthor.objects.prefetch_related('timeline_set').filter(
            timeline_bertopic_id__isnull=True, has_timeline=True, platform=platform).filter(
            timeline__lang=language).annotate(
            timeline_text=StringAgg('timeline__text', delimiter='.'))

    timeline_text_dict = {}
    for tweet_author in tweet_authors:
        timeline_text_dict[tweet_author.id] = tweet_author.timeline_text
    for tweet_authors in batch(list(tweet_authors.all()), 1000):
        author_texts = []
        for tweet_author in tweet_authors:
            author_texts.append(timeline_text_dict[tweet_author.id])
        author_texts_cleaned = clean_corpus(author_texts)

        n_texts = len(author_texts_cleaned)
        n_authors = len(tweet_authors)
        assert n_texts == n_authors
        if len(author_texts_cleaned) > 0:
            classifications = bertopic_model.transform(author_texts_cleaned)
            topic_classifications = classifications[0]
            index = 0
            tweet_author_length = len(tweet_authors)
            classification_length = len(topic_classifications)
            assert tweet_author_length == classification_length
            for tweet_author in tweet_authors:
                if topic_classifications[index] in topic_info.Topic:
                    tweet_author.timeline_bertopic_id = topic_classifications[index]
                else:
                    tweet_author.timeline_bertopic_id = -2
                index += 1
            TweetAuthor.objects.bulk_update(tweet_authors, ["timeline_bertopic_id"])
        # set all tweets that don't have a timeline to -3
        tweet_authors = TweetAuthor.objects.filter(has_timeline=False).all()
        for tweet_author in tweet_authors:
            tweet_author.timeline_bertopic_id = -3
        TweetAuthor.objects.bulk_update(tweet_authors, ["timeline_bertopic_id"])
