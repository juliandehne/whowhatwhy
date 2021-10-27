from delab.topic.topic_algorithm_context_free import calculate_topic_flow


def run():
    calculate_topic_flow(train=True, store_vectors=False, store_topics=True, update_topics=True)
