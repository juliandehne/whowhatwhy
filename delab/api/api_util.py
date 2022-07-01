from django_pandas.io import read_frame

from delab.models import Tweet


def get_standard_field_names():
    return ["twitter_id",
            "conversation_id",
            "author_id",
            "created_at",
            "in_reply_to_user_id",
            "text", "tw_author__name", "tw_author__location", "topic__title"]


def get_file_name(conversation_id, full, suffix):
    return str(conversation_id) + "_conversation_" + full + suffix


def get_all_conversation_ids(topic=None):
    if topic is not None:
        result = Tweet.objects.filter(topic__title=topic).distinct(
            "conversation_id").values_list("conversation_id",
                                           flat=True).all()
    else:
        result = Tweet.objects.distinct("conversation_id").values_list("conversation_id",
                                                                       flat=True).all()
    result = list(result)
    return result


def get_conversation_dataframe(topic_string: str, conversation_id: int = None):
    if conversation_id is not None:
        qs = Tweet.objects.filter(conversation_id=conversation_id, topic__title=topic_string).all()
    else:
        qs = Tweet.objects.filter(topic__title=topic_string).all()
    df = add_parents_to_frame(qs)
    return df


def add_parents_to_frame(qs):
    """
    There seems to be bug in the django-pandas api that self-foreign keys are not returned properly
    This is a workaround
    :param qs:
    :return:
    """
    tn_parent_ids = qs.values_list("tn_parent_id", flat=True).all()
    df = read_frame(qs.all(), fieldnames=get_standard_field_names(), verbose=True)
    df['tn_parent_id'] = tn_parent_ids
    df['tn_parent_id'] = df['tn_parent_id'].astype('Int64')
    df['in_reply_to_user_id'] = df['in_reply_to_user_id'].astype('Int64')
    return df


class ConversationFilter:
    max_orphan_count = 4
    min_depth = 3
    merge_subsequent = True
