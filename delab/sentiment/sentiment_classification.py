# import Layer from the utils.py file
import json
import logging

import numpy as np
from django.db.models import Q

from delab.models import SADictionary, Tweet
from delab.sentiment.sentiment_model import TASK_DESCRIPTION, classifier, get_model_path, tweet_to_tensor


def update_tweet_sentiments(simple_request_id=-1):
    """
    Home brew sentiment classification using trax might be replaced with a pre-build sentiment classifier
    :param simple_request_id:
    :return:
    """

    from delab.sentiment.sentiment_classification import classify_tweet_sentiment
    from delab.sentiment.sentiment_training import update_dictionary

    if simple_request_id < 0:
        tweets = Tweet.objects.filter(
            (Q(sentiment=None) | Q(sentiment_value=None)) & ~Q(sentiment="failed_analysis")).all()
    else:
        tweets = Tweet.objects.filter(Q(simple_request_id=simple_request_id) &
                                      (Q(sentiment=None) | Q(sentiment_value=None)) &
                                      ~Q(sentiment="failed_analysis")).all()
    # tweet_strings = tweets.values_list(["text"], flat=True)
    # print(tweet_strings[1:3])
    tweet_strings = list(map(lambda x: x.text, tweets))
    update_dictionary(tweet_strings)
    predictions, sentiments, sentiment_values = classify_tweet_sentiment(tweet_strings)
    for tweet in tweets:
        tweet.sentiment = sentiments.get(tweet.text, "failed_analysis")
        tweet.sentiment_value = sentiment_values.get(tweet.text, None)
        tweet.save()


## not implemented, just ofr later use trained sentiment classifier using BERT
def classify_german_sentiment(tweet_string):
    '''
    from germansentiment import SentimentModel

    model = SentimentModel()

    texts = [
        "Mit keinem guten Ergebniss", "Das ist gar nicht mal so gut",
        "Total awesome!", "nicht so schlecht wie erwartet",
        "Der Test verlief positiv.", "Sie fährt ein grünes Auto."]

    result = model.predict_sentiment(texts)
    print(result)
    '''


def classify_tweet_sentiment(tweet_strings, verbose=False):
    logger = logging.getLogger(__name__)
    """ classifies the sentiment of a tweet based on classic NLP example with trax

        Parameters
        ----------
        tweet_strings :  [str]
            List of tweets as string that are to be classified        

        Returns
        -------
         prediction_dictionary :  dict
            keys are the tweets as string and values are the predicted values
         sentiment_dictionary: dict
            keys are the tweets as string and values are the sentiment
    """

    # Initialize using pre-trained weights.

    django_dictionary = SADictionary.objects.all().filter(title=TASK_DESCRIPTION).get()
    vocab_dict = json.loads(django_dictionary.dictionary_string)

    model = classifier(len(vocab_dict))
    model.init_from_file(get_model_path() + "model.pkl.gz")

    prediction_dictionary = {}
    sentiment_dictionary = {}
    sentiment_value_dictionary = {}

    for tweet_string in tweet_strings:
        try:
            predictions, sentiment, sentiment_value = predict(tweet_string, model, vocab_dict)
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


# this is used to predict on your own sentence
def predict(sentence, model, vocab_dict):
    inputs = np.array(tweet_to_tensor(sentence, vocab_dict=vocab_dict))

    # Batch size 1, add dimension for batch, to work with the model
    inputs = inputs[None, :]

    # predict with the model
    preds_probs = model(inputs)

    # combine the probabilities into one dimension (higher is positiver)
    sentiment_value = preds_probs[0, 1] - preds_probs[0, 0]

    # Turn probabilities into categories
    preds = int(preds_probs[0, 1] > preds_probs[0, 0])

    sentiment = "negative"
    if preds == 1:
        sentiment = 'positive'

    return preds_probs, sentiment, sentiment_value
