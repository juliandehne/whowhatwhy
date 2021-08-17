from delab.tasks import update_sentiments

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""


def run():
    tweet_negative = "I really hate this crap"
    tweet_positive = "love love love happiness great awesome story"
    tweet_strings = ["This movie was almost good", tweet_negative, tweet_positive]
    # classify_tweet_sentiment(tweet_strings)

    update_sentiments()
    # figure_out_weights()


def figure_out_weights():
    from delab.sentiment_classification import classify_tweet_sentiment

    tweet_negative = "I really hate this crap"
    tweet_positive = "love love love happiness great awesome story"
    tweet_strings = ["This movie was almost good", tweet_negative, tweet_positive]

    predictions, sentiments = classify_tweet_sentiment(tweet_strings, verbose=True)
