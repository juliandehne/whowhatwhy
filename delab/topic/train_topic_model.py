import logging
import os
import sqlite3

from django.db.models import Q
from django_pandas.io import read_frame

from delab.models import Timeline, Tweet
from bertopic import BERTopic
from util import TVocabulary


def train_topic_model_from_db(lang="en"):
    author_tweets_texts, logger = load_author_tweets(lang)
    conversation_tweets_texts = load_conversation_tweets(lang, logger)
    corpus_for_fitting_sentences = create_tweet_corpus_for_bertopic(author_tweets_texts, conversation_tweets_texts)

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    topic_model_2 = BERTopic(embedding_model="sentence-transformers/all-mpnet-base-v2", verbose=True)
    topics, probs = topic_model_2.fit_transform(corpus_for_fitting_sentences)

    vocab = create_vocabulary(corpus_for_fitting_sentences)

    bad_topics = get_bad_topics(vocab, topic_model_2)

    topic_info = topic_model_2.get_topic_info()
    mask = topic_info["Topic"].isin(bad_topics)
    mask = mask[mask == True]
    topic_info.drop(index=mask.index, inplace=True)

    model_location_name = "BERTopic"
    topic_model_2.save(model_location_name)
    return model_location_name


def create_vocabulary(corpus_for_fitting_sentences):
    vocab = TVocabulary()
    for corpus_for_fitting_sentence in corpus_for_fitting_sentences:
        vocab.add_sentence(corpus_for_fitting_sentence)
    return vocab


def create_tweet_corpus_for_bertopic(author_tweets_texts, conversation_tweets_texts):
    corpus_for_fitting = author_tweets_texts + conversation_tweets_texts
    # corpus_for_fitting = author_tweets_texts
    corpus_for_fitting_sentences = []
    for tweet in corpus_for_fitting:
        for sentence in tweet.split("."):
            corpus_for_fitting_sentences.append(sentence)
    return corpus_for_fitting_sentences


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
    logger = logging.getLogger(__name__)
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
