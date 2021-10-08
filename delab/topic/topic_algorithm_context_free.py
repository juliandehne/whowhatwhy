"""
1. Create a seperate file and run the bert_topic fitting there, call this function with train = True for testing
    a) run the fitting [x]
    b) use the bert_topic transform to get all the the topic words [x]
    c) get embedding vectors from fasttest using the topic words [x]
    d) store the embeddings vectors in database [x]
    e) store the bert_topic model [x]
2. Calculate conversation flow (this file)
    a) load the bert_topic model [x]
    b) classify the tweets, and store the model_id/topic_id in the db
    c) create dictionary (tweet: topic)
    d) create a dictionary (topic_1, topic_2) -> distance (by loading fasttext vectors for the tweets and cosine)
    e) create a dictionary (tweet_1,tweet_2) -> distance (standardizing the topic distances and using i-1 for not defined topic)
    f) calculate the rolling average topic change for the conversation using the same method as with sentiment
    g) plot the the topic_changes alongside the conversation flow_changes
    h) store the updated picture alongside the sentiment one

"""
import json

from bertopic import BERTopic
from django.db.models import Q

import delab.topic.train_topic_model as tm
import fasttext.util

from util import TVocabulary

from delab.models import TopicDictionary, Tweet
import numpy as np
import logging


# TODO implement this as part of the pipeline

def calculate_topic_flow(train=False, bertopic_location=tm.BERTOPIC_MODEL_LOCATION, lang="en", store_vectors=True,
                         store_topics=True, update_topics=False):
    """ This function takes the tweets of the authors' conversations and uses them as a context for the authors'
        regular topics. They are analyzed by how related their NER are.
    """

    logging.getLogger('numba').setLevel(logging.WARNING)

    if train:
        bertopic_location = tm.train_topic_model_from_db(lang,
                                                         store_vectors=store_vectors,
                                                         store_topics=store_topics,
                                                         update_topics=update_topics)

    bertopic_model = BERTopic().load(bertopic_location, embedding_model="sentence-transformers/all-mpnet-base-v2")

    # get the filtered topic model
    topic_info = tm.filter_bad_topics(bertopic_model, tm.get_vocab(lang))

    # calculate distances

    # restore as json.loads with a_restored = np.asarray(json_load["a"])
