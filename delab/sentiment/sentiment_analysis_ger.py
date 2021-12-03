from germansentiment import SentimentModel


def classify_german_sentiments(texts):
    model = SentimentModel()

    result = model.predict_sentiment(texts)

    prediction_dictionary = {}
    sentiment_dictionary = {}
    sentiment_value_dictionary = {}

    predictions = -1
    sentiment_value = 0

    index = 0
    for sentiment in result:
        tweet_string = texts[index]
        if sentiment == "positive":
            predictions = 1
            sentiment_value = 1
        if sentiment == "negative":
            predictions = 0
            sentiment_value = -1

        prediction_dictionary[tweet_string] = predictions
        sentiment_dictionary[tweet_string] = sentiment
        sentiment_value_dictionary[tweet_string] = sentiment_value
        index += 1

    return prediction_dictionary, sentiment_dictionary, sentiment_value_dictionary
