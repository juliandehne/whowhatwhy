from twitter.sentiment_analysis import classify_tweet_sentiment

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""


def run():
    # tweet = "I really love hot bagels and I do not hate ice cream"
    # tweet = "love love love happiness great awesome story"
    # tweet = "if only it was a good day."
    tweet = "This movie was almost good"
    classify_tweet_sentiment(tweet)
