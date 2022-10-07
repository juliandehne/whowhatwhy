from delab.corpus.download_author_information import update_authors
from delab.delab_enums import VERSION, PLATFORM, LANGUAGE
from delab.sentiment.sentiment_classification import update_tweet_sentiments
from delab.topic.topic_data_preperation import update_timelines_from_conversation_users
from delab.topic.train_topic_model import classify_author_timelines, train_topic_model_from_db, classify_tweet_topics


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
        print("STEP 1.1: updated tweet sentiments")
        # download the extended author data for those who are missing
        update_authors(platform=PLATFORM.TWITTER)
        # update_authors(platform=PLATFORM.REDDIT)
        print("STEP 2: FINISHED updating authors")
        # download the twitter timelines for those who are missing
        update_timelines_from_conversation_users(platform=PLATFORM.TWITTER)
        update_timelines_from_conversation_users(platform=PLATFORM.REDDIT)
        print("STEP 3: FINISHED updating author timelines")
        # 1. Trains the bertopic model on the timelines and the tweets and stores the trained bertopic model in "BERTopic"
        # 2. loads fasttextvectors for all bertopic models and stores them in topicdictionary
        train_topic_model_from_db(version=analysis_version,
                                  train=train_update_topics,
                                  store_vectors=train_update_topics,
                                  number_of_batches=1000,
                                  platform=PLATFORM.TWITTER,
                                  language=LANGUAGE.ENGLISH)
        train_topic_model_from_db(version=analysis_version,
                                  train=train_update_topics,
                                  store_vectors=train_update_topics,
                                  number_of_batches=1000,
                                  platform=PLATFORM.TWITTER,
                                  language=LANGUAGE.GERMAN)
        train_topic_model_from_db(version=analysis_version,
                                  train=train_update_topics,
                                  store_vectors=train_update_topics,
                                  number_of_batches=1000,
                                  platform=PLATFORM.REDDIT,
                                  language=LANGUAGE.ENGLISH)
    train_topic_model_from_db(version=analysis_version,
                              train=train_update_topics,
                              store_vectors=train_update_topics,
                              number_of_batches=1000,
                              platform=PLATFORM.REDDIT,
                              language=LANGUAGE.GERMAN)

    print("STEP 4: FINISHED training the bertopic model")
    # classify the author timelines
    classify_author_timelines(version=analysis_version, language=LANGUAGE.GERMAN, update=train_update_topics,
                              platform=PLATFORM.REDDIT)
    classify_author_timelines(version=analysis_version, language=LANGUAGE.ENGLISH, update=train_update_topics,
                              platform=PLATFORM.TWITTER)

    print("STEP 5: FINISHED classifying the author timelines")
    # classifying the tweets
    classify_tweet_topics(analysis_version, LANGUAGE.ENGLISH, update_topics=train_update_topics,
                          platform=PLATFORM.TWITTER)
    classify_tweet_topics(analysis_version, LANGUAGE.GERMAN, update_topics=train_update_topics,
                          platform=PLATFORM.REDDIT)
