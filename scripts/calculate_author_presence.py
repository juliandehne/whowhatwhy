from delab.api.api_util import get_all_conversation_ids


def run():
    required_max_path_length = 4
    min_path_length = 3

    conversation_ids = get_all_conversation_ids()
    count = 0
    for conversation_id in conversation_ids:
        count += 1
        print("processed {}/{} conversations".format(count, len(conversation_ids)))
