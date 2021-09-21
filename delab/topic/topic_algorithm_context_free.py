"""
1. Create a seperate file and run the bert_topic fitting there, call this function with train = True for testing
    a) run the fitting
    b) use the bert_topic transform to get all the the topic words
    c) get embedding vectors from fasttest using the topic words
    d) store the embeddings vectors in database
    e) store the bert_topic model
2. Calculate conversation flow (this file)
    a) load the bert_topic model
    b) classify the tweets, and store the model_id/topic_id in the db
    c) create dictionary (tweet: topic)
    d) create a dictionary (topic_1, topic_2) -> distance (by loading fasttext vectors for the tweets and cosine)
    e) create a dictionary (tweet_1,tweet_2) -> distance (standardizing the topic distances and using i-1 for not defined topic)
    f) calculate the rolling average topic change for the conversation using the same method as with sentiment
    g) plot the the topic_changes alongside the conversation flow_changes
    h) store the updated picture alongside the sentiment one

"""


def calculate_topic_flow(train=False):
    """ This function takes the tweets of the authors' conversations and uses them as a context for the authors'
        regular topics. They are analyzed by how related their NER are.
    """
    pass