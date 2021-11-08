import json
import logging
import os
import sqlite3

import numpy as np
from django.db.models import Q
from django_pandas.io import read_frame

from delab.models import Timeline, Tweet
from bertopic import BERTopic

import fasttext.util

from util import TVocabulary

from delab.models import TopicDictionary

BERTOPIC_MODEL_LOCATION = "BERTopic"

logger = logging.getLogger(__name__)


def train_topic_model_from_db(lang="en", store_vectors=True, store_topics=True, update_topics=True):
    logger.debug("starting to train the topic model")
    corpus_for_fitting_sentences = get_train_corpus_for_sentences(lang)

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    topic_model_2 = BERTopic(embedding_model="sentence-transformers/all-mpnet-base-v2", verbose=True)
    topics, probs = topic_model_2.fit_transform(corpus_for_fitting_sentences)

    if store_vectors or store_topics:
        vocab = create_vocabulary(corpus_for_fitting_sentences)
        if store_vectors:
            store_embedding_vectors(topic_model_2, vocab, lang)

        if store_topics:
            store_topic_id_tweets(topic_model_2, lang, update_topics, vocab)

    topic_model_2.save(BERTOPIC_MODEL_LOCATION)
    logger.debug("finished training the topic model")
    return BERTOPIC_MODEL_LOCATION


def filter_bad_topics(bertopic_model, vocab):
    bad_topics = get_bad_topics(vocab, bertopic_model)
    topic_info = bertopic_model.get_topic_info()
    mask = topic_info["Topic"].isin(bad_topics)
    mask = mask[mask == True]
    topic_info.drop(index=mask.index, inplace=True)
    return topic_info


def store_embedding_vectors(bertopic_model, vocab, lang):
    # fasttext.load_model('cc.en.300.bin') # comment this in instead of the next line, if you are not Julian
    ft = fasttext.load_model('/home/julian/nltk_data/fasttext/cc.{}.300.bin'.format(lang))

    # filter topics
    topic_info = filter_bad_topics(bertopic_model, vocab)

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
                TopicDictionary.objects.get_or_create(word=str_w, ft_vector=json.dumps(ft_vector, cls=NumpyEncoder))
    print("saved ft_vectors. The hit rate was: {}".format(n_words_in_voc / (n_words_in_voc + n_words_nin_voc)))


def get_bad_topics(vocab, topic_model_2):
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


def get_vocab(lang):
    sentences = get_train_corpus_for_sentences(lang)
    vocab = create_vocabulary(sentences)
    return vocab


def get_train_corpus_for_sentences(lang):
    author_tweets_texts, logger = load_author_tweets(lang)
    conversation_tweets_texts = load_conversation_tweets(lang, logger)
    corpus_for_fitting_sentences = create_tweet_corpus_for_bertopic(author_tweets_texts, conversation_tweets_texts)
    return corpus_for_fitting_sentences


def create_tweet_corpus_for_bertopic(author_tweets_texts, conversation_tweets_texts):
    corpus_for_fitting = author_tweets_texts + conversation_tweets_texts
    # corpus_for_fitting = author_tweets_texts
    corpus_for_fitting_sentences = []
    for tweet in corpus_for_fitting:
        for sentence in tweet.split("."):
            corpus_for_fitting_sentences.append(sentence)
    return corpus_for_fitting_sentences


def store_topic_id_tweets(bertopic_model, lang, update_topics, vocab):
    # load tweets
    topic_info = filter_bad_topics(bertopic_model, vocab)
    if update_topics:
        conversation_tweets = Tweet.objects.filter(Q(language=lang)).all()
    else:
        conversation_tweets = Tweet.objects.filter(Q(language=lang) & Q(bertopic_id__isnull=True)).all()

    for conversation_tweet in conversation_tweets:
        suggested_topics2 = bertopic_model.transform(conversation_tweet.text)
        np_suggested_topics2 = np.array(suggested_topics2[0])
        if np_suggested_topics2[0] in topic_info.Topic:
            conversation_tweet.bertopic_id = np_suggested_topics2[0]
        else:
            conversation_tweet.bertopic_id = -2
        conversation_tweet.save(update_fields=["bertopic_id"])


def load_conversation_tweets(lang, logger):
    conversation_tweets = Tweet.objects.filter(Q(language=lang)).all()
    df_conversations = read_frame(conversation_tweets, fieldnames=["id",
                                                                   "author_id",
                                                                   "text",
                                                                   ])
    logger.info("loaded the timeline from the database")
    conversation_tweets_texts = list(df_conversations.text)
    return conversation_tweets_texts


def load_author_tweets(lang):
    tweets = Timeline.objects.filter(Q(lang=lang)).all()
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
