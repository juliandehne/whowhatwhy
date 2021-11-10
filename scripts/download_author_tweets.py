from delab.topic.topic_data_preperation import update_timelines_from_conversation_users


def run(*args):
    if len(args) == 1:
        update_timelines_from_conversation_users(classify_author_topics=(args[0] == "True"))
    if len(args) == 2:
        update_timelines_from_conversation_users(classify_author_topics=(args[0] == "True"),
                                                 update_author_topics=(args[1] == "True"))
    else:
        update_timelines_from_conversation_users()
