from delab.corpus.download_author_information import update_authors
from delab.delab_enums import VERSION, PLATFORM, LANGUAGE
from delab.sentiment.sentiment_classification import update_tweet_sentiments


def run():
    """
    for each parent and child in a conversation this computes deltas of the tweet specific measures like sentiment
    and stores it in the ConversationFlowMetric table
    :return:
    """

    analysis_version = VERSION.v005
    train_update_topics = True
    preparation = False

    if preparation:
        update_tweet_sentiments(language=LANGUAGE.ENGLISH)
        update_tweet_sentiments(language=LANGUAGE.GERMAN)
        print("STEP 1 FINISHED: updated tweet sentiments")
        # download the extended author data for those who are missing
        update_authors(platform=PLATFORM.TWITTER)
        # update_authors(platform=PLATFORM.REDDIT)
        print("STEP 2 FINISHED: updating authors")
        # download the twitter timelines for those who are missing
