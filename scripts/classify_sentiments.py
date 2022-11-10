from delab.delab_enums import LANGUAGE
from delab.sentiment.sentiment_classification import classify_tweet_sentiment, update_tweet_sentiments
from delab.tasks import update_sentiments
from delab.toxicity.perspectives import compute_toxicity_for_text

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""


def run(*args):
    # some_test_cases(args)

    # update_tweet_sentiments()
    # update_tweet_sentiments(language=LANGUAGE.GERMAN)
    compute_toxicity_for_text()


def some_test_cases(args):
    tweet_negative = "I really hate this crap"
    tweet_negative_2 = "I really don't hate this"
    tweet_negative_3 = "I really don't love this"
    tweet_positive = "love love love happiness great awesome story"
    tweet_strings = ["This movie was almost good", "This movie was good almost", "Movie was good almost",
                     "This movie was good and a lot happened it between things like that almost",
                     "This movie was almost good and very little happened it between things like that",
                     tweet_negative, tweet_positive, tweet_negative_2, tweet_negative_3]
    if len(args) == 1:
        language = args[0]
        if language == LANGUAGE.GERMAN:
            tweet_strings = [
                "Mit keinem guten Ergebniss", "Das ist gar nicht mal so gut",
                "Total awesome!", "nicht so schlecht wie erwartet",
                "Der Test verlief positiv.", "Sie fährt ein grünes Auto."]
        classify_tweet_sentiment(tweet_strings, verbose=True, language=language)
    else:
        classify_tweet_sentiment(tweet_strings, verbose=True, language=LANGUAGE.ENGLISH)


def figure_out_weights():
    from delab.sentiment.sentiment_classification import classify_tweet_sentiment

    tweet_negative = "I really hate this crap"
    tweet_positive = "love love love happiness great awesome story"
    tweet_strings = ["This movie was almost good", tweet_negative, tweet_positive]

    predictions, sentiments = classify_tweet_sentiment(tweet_strings, verbose=True)
