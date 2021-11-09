from delab.topic.train_topic_model import train_topic_model_from_db


def run(*args):
    """
    Run this with
    runscript calculate_topic_similarities --script-args 1000 True
    :param args: number of batches (-1 for all), True/False whether to retrain the bert model
    :return:
    """
    print(args)
    if len(args) == 1:
        train_topic_model_from_db(train=True, store_vectors=True, store_topics=True, update_topics=True,
                                  number_of_batchs=int(args[0]))
    if len(args) == 2:
        train_topic_model_from_db(train=bool(args[1] == "True"), store_vectors=True, store_topics=True,
                                  update_topics=True,
                                  number_of_batchs=int(args[0]))
    else:
        train_topic_model_from_db(train=True, store_vectors=True, store_topics=True, update_topics=True)
