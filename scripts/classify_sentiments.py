from delab.sentiment.sentiment_classification import classify_tweet_sentiment

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""


def run():
    tweet_negative = "I really hate this crap"
    tweet_negative_2 = "I really don't hate this"
    tweet_negative_3 = "I really don't love this"
    tweet_positive = "love love love happiness great awesome story"
    tweet_strings = ["This movie was almost good", "This movie was good almost", "Movie was good almost",
                     "This movie was good and a lot happened it between things like that almost",
                     "This movie was almost good and very little happened it between things like that",
                     tweet_negative, tweet_positive, tweet_negative_2, tweet_negative_3]
    classify_tweet_sentiment(tweet_strings, verbose=True)

    # update_sentiments()
    # figure_out_weights()


def figure_out_weights():
    from delab.sentiment.sentiment_classification import classify_tweet_sentiment

    tweet_negative = "I really hate this crap"
    tweet_positive = "love love love happiness great awesome story"
    tweet_strings = ["This movie was almost good", tweet_negative, tweet_positive]

    predictions, sentiments = classify_tweet_sentiment(tweet_strings, verbose=True)
