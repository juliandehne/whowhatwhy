"""
This pipeline computes the full analysis of the downloaded tweets
1. download the missing authordata and timelines (if that has not happened)
2. analyse the sentiments of the tweets
3. compute data for the candidate table
"""
from delab.corpus.download_author_information import update_authors
from delab.sentiment.sentiment_training import train_sentiment_classification
from delab.topic.topic_data_preperation import update_timelines_from_conversation_users
from delab.topic.train_topic_model import classify_author_timelines, train_topic_model_from_db


def run(*args):
    analysis_version = "v0.0.1"
    if len(args) > 0:
        analysis_version = args[0]

    # Stores the trained sentiment model in {base}/model
    # train_sentiment_classification()
    # download the extended author data for those who are missing
    update_authors()
    # download the twitter timelines for those who are missing
    update_timelines_from_conversation_users()

    # 1. Trains the bertopic model on the timelines and the tweets and stores the trained bertopic model in "BERTopic"
    # 2. loads fasttextvectors for all bertopic models and stores them in topicdictionary
    # 3. classifies all tweets with a bertopic model
    train_topic_model_from_db()
    # classify the author timelines
    classify_author_timelines()



