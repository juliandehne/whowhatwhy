from delab.delab_enums import VERSION, PLATFORM, LANGUAGE
from delab.topic.train_topic_model import train_topic_model_from_db, classify_tweet_topics


def run():
    """
    this computes bertopic models for the delab based topic related queries
    :return:
    """
    analysis_version = VERSION.v001
    platform = PLATFORM.TWITTER
    train_update_topics = True
    topic = "right_wing"

    train_topic_model_from_db(version=analysis_version,
                              train=train_update_topics,
                              store_vectors=False,
                              number_of_batches=1000,
                              platform=platform,
                              language=LANGUAGE.ENGLISH,
                              topic=topic)
    train_topic_model_from_db(version=analysis_version,
                              train=train_update_topics,
                              store_vectors=False,
                              number_of_batches=1000,
                              platform=platform,
                              language=LANGUAGE.GERMAN,
                              topic=topic)

    # classifying the tweets
    classify_tweet_topics(analysis_version, LANGUAGE.ENGLISH, update_topics=train_update_topics, platform=platform,
                          topic=topic)
    classify_tweet_topics(analysis_version, LANGUAGE.GERMAN, update_topics=train_update_topics, platform=platform,
                          topic=topic)
