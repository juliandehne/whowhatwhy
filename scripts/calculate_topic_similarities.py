import sqlite3

import fasttext.util
import pandas as pd
from django.db.models import Q
from django.utils.baseconv import base64
import pickle
from django_pandas.io import read_frame
import fasttext.util
from tqdm import tqdm

from delab.models import Timeline
import logging


def run():
    logger = logging.getLogger(__name__)
    cnx = sqlite3.connect('../db.sqlite3')
    # df = pd.read_sql_query("SELECT id, conversation_id, created_at, text, author_id,in_reply_to_user_id FROM delab_timeline WHERE lang='en'", cnx)
    # df.head(3)
    tweets = Timeline.objects.filter(Q(lang="en") & Q(ft_vector_dump__isnull=True)).all()
    df = read_frame(tweets, fieldnames=["id",
                                        "author_id",
                                        "text",
                                        "conversation_id",
                                        "created_at",
                                        ])
    logger.info("loaded the timeline from the database")
    # %%

    # group by the authors

    df_reduced = df[["author_id", "text", "id"]]
    df_reshaped = df_reduced.pivot(index="id", columns="author_id", values="text")
    mask = 400 > df_reshaped.nunique()
    mask = mask[mask == True]
    df_reshaped.drop(columns=mask.index, inplace=True)
    df_reshaped.nunique()

    # reshape to a dictionary with authors as keys and their tweets as values

    author_corpora_cleaned = {}
    author_corpora = df_reshaped.to_dict(orient="series")
    for author_id, tweets in author_corpora.items():
        author_corpora_cleaned[author_id] = tweets.dropna()
    # fasttext.load_model('cc.en.300.bin') # comment this in instead of the next line, if you are not Julian

    # clean authors tweets

    author_words_uncleaned = []
    for author, a_tweets in author_corpora_cleaned.items():
        for a_tweet in a_tweets:
            for word in a_tweet.split(" "):
                author_words_uncleaned.append(word)

    n_words = len(author_words_uncleaned)
    print("{} uncleaned words are in the input. For example: ".format(n_words))
    print(author_words_uncleaned[:5])

    # count the oov
    ft = fasttext.load_model('/home/julian/nltk_data/fasttext/cc.de.300.bin')
    print("loaded the embeddings")
    n_words_in_voc = 0
    in_voc_words = set()
    for word in tqdm(author_words_uncleaned):
        if word in ft.words:
            n_words_in_voc += 1
            # np_bytes = pickle.dumps(word_vec_example)
            # np_base64 = base64.b64encode(np_bytes)
            # store it in db here...
            # unloading it
            # np_array = pickle.loads(np_bytes)

    print(
        "The accuracy, that uncleaned words are in the embedding vocabulary is {}.".format((n_words_in_voc / n_words)))

