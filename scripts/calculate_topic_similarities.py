from delab.topic.topic_algorithm_context_free import calculate_topic_flow


def run(*args):
    print(args)
    if len(args) > 0:
        calculate_topic_flow(train=True, store_vectors=True, store_topics=True, update_topics=True,
                             number_of_batchs=int(args[0]))
    else:
        calculate_topic_flow(train=True, store_vectors=True, store_topics=True, update_topics=True)
