import itertools

import networkx as nx

from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_sequences import get_all_reply_paths, get_path
from delab.models import Tweet


def run():
    required_max_path_length = 4
    min_path_length = 3

    conversation_ids = get_all_conversation_ids()
    count = 0
    for conversation_id in conversation_ids:
        count += 1
        print("processed {}/{} conversations".format(count, len(conversation_ids)))
        all_paths = get_all_reply_paths(conversation_id, min_path_length, required_max_path_length)

        if len(all_paths) > 10:
            for path in all_paths:
                print(path)
            print("####")
            print(get_path(20591832, conversation_id, min_path_length, required_max_path_length))
            break


