"""
1. Create a seperate file and run the bert_topic fitting there, call this function with train = True for testing
    a) run the fitting
    b) use the bert_topic transform to get all the the topic words
    c) get embedding vectors from fasttest using the topic words
    d) store the embeddings vectors in database
    e) store the bert_topic model
2. Calculate conversation flow (this file)
    a) load the bert_topic model
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

import delab.topic.train_topic_model
import fasttext.util

from delab.models import TopicDictionary
import numpy as np
import logging


def calculate_topic_flow(train=False, bertopic_location="berttopic_1", lang="en"):
    """ This function takes the tweets of the authors' conversations and uses them as a context for the authors'
        regular topics. They are analyzed by how related their NER are.
    """

    logging.getLogger('numba').setLevel(logging.WARNING)

    if train:
        bertopic_location = delab.topic.train_topic_model.train_topic_model_from_db(lang)

    # topic_model = BERTopic(embedding_model="sentence-transformers/all-mpnet-base-v2", verbose=True)
    topic_model = BERTopic().load(bertopic_location, embedding_model="sentence-transformers/all-mpnet-base-v2")
    topic_info = topic_model.get_topic_info()

    # fasttext.load_model('cc.en.300.bin') # comment this in instead of the next line, if you are not Julian
    ft = fasttext.load_model('/home/julian/nltk_data/fasttext/cc.{}.300.bin'.format(lang))

    n_words_nin_voc = 0
    n_words_in_voc = 0
    for topic_id in topic_info.Topic:
        topic_model = topic_model.get_topic(topic_id)
        for t_word in topic_model:
            str_w = t_word[0]
            if str_w not in ft.words:
                n_words_nin_voc += 1
            else:
                n_words_in_voc += 1
                ft_vector = ft.get_word_vector(str_w)
                TopicDictionary.objects.get_or_create(word=str_w, ft_vector=json.dumps(ft_vector, cls=NumpyEncoder))
    print("saved ft_vectors. The hit rate was: {}".format(n_words_in_voc / (n_words_in_voc + n_words_nin_voc)))

    # restore as json.loads with a_restored = np.asarray(json_load["a"])


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
