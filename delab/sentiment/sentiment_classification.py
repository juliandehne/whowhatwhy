# import Layer from the utils.py file
import logging

from django.db.models import Q
from nltk.sentiment import SentimentIntensityAnalyzer

from delab.models import Tweet
from delab.delab_enums import LANGUAGE
from delab.sentiment.sentiment_analysis_ger import classify_german_sentiments


def update_tweet_sentiments(simple_request_id=-1, language=LANGUAGE.ENGLISH):
    if simple_request_id < 0:
        tweets = Tweet.objects.filter(Q(language=language) &
                                      (Q(sentiment=None) | Q(sentiment_value=None)) & ~Q(
            sentiment="failed_analysis")).all()
    else:
        tweets = Tweet.objects.filter(Q(simple_request_id=simple_request_id) & Q(language=language) &
                                      (Q(sentiment=None) | Q(sentiment_value=None)) &
                                      ~Q(sentiment="failed_analysis")).all()
    # tweet_strings = tweets.values_list(["text"], flat=True)
    # print(tweet_strings[1:3])
    tweet_strings = list(map(lambda x: x.text, tweets))

    predictions, sentiments, sentiment_values = classify_tweet_sentiment(tweet_strings)
    for tweet in tweets:
        tweet.sentiment = sentiments.get(tweet.text, "failed_analysis")
        tweet.sentiment_value = sentiment_values.get(tweet.text, None)
    Tweet.objects.bulk_update(tweets, ["sentiment", "sentiment_value"])


def classify_tweet_sentiment(tweet_strings, verbose=False, language=LANGUAGE.ENGLISH):
    if language == LANGUAGE.GERMAN:
        return classify_german_sentiments(tweet_strings)

    logger = logging.getLogger(__name__)

    # Initialize using pre-trained weights.
    prediction_dictionary = {}
    sentiment_dictionary = {}
    sentiment_value_dictionary = {}

    return predict_sentiments_en(logger, prediction_dictionary, sentiment_dictionary, sentiment_value_dictionary,
                                 tweet_strings, verbose)


def predict_sentiments_en(logger, prediction_dictionary, sentiment_dictionary, sentiment_value_dictionary,
                          tweet_strings, verbose):
    sia = SentimentIntensityAnalyzer()
    for tweet_string in tweet_strings:
        try:
            polarity_scores = sia.polarity_scores(tweet_string)
            sentiment_value = polarity_scores.get("compound", 0)
            if sentiment_value > 0:
                predictions = 1
                sentiment = "positive"
            else:
                predictions = 0
                sentiment = "negative"
            if sentiment_value == 0:
                predictions = -1
                sentiment = "neutral"
            if verbose:
                logger.debug(
                    "the tweet \"{}\" was predicted as \"{}\" with the values {}".format(tweet_string, sentiment,
                                                                                         sentiment_value))
            prediction_dictionary[tweet_string] = predictions
            sentiment_dictionary[tweet_string] = sentiment
            sentiment_value_dictionary[tweet_string] = sentiment_value
        except:
            logger.error("could not analyze sentiment of: {} ".format(tweet_string))
            continue
    return prediction_dictionary, sentiment_dictionary, sentiment_value_dictionary
