from delab.sentiment_training import classify_tweet_sentiment, train_sentiment_classification

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""


def run():
    train_sentiment_classification()
