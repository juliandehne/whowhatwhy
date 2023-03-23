from more_itertools import take

from delab.analytics.cccp_analytics import compute_missing_authors, create_n_count_dict
from delab.models import ConversationAuthorMetrics, Tweet


def run():
    all_conversation_ids = Tweet.objects.values_list('conversation_id', flat=True)
    computed_conversation_ids = ConversationAuthorMetrics.objects.values_list('conversation_id', 'n_posts')

    all_dict = {}
    for conversation_id in all_conversation_ids:
        if conversation_id in all_dict:
            all_dict[conversation_id] += 1
        else:
            all_dict[conversation_id] = 1
    computed_dict = {}
    for conversation_id, n_post in computed_conversation_ids:
        if conversation_id in computed_dict:
            computed_dict[conversation_id] = computed_dict[conversation_id] + n_post
        else:
            computed_dict[conversation_id] = n_post

    n_count_dict = create_n_count_dict()
    computed_conversations = []
    for conversation_id in all_conversation_ids:
        if conversation_id in computed_conversations:
            continue
        if conversation_id not in computed_dict:
            print("for conversation " + str(conversation_id) + "  " + str(all_dict[conversation_id]) + " tweets were never computed")
            compute_missing_authors(conversation_id, n_count_dict)
        elif all_dict[conversation_id] != computed_dict[conversation_id]:
            diff = all_dict[conversation_id] - computed_dict[conversation_id]
            print("for conversation " + str(conversation_id) + " " + str(diff) + " tweets weren't computed")
            print("computed: " + str(computed_dict[conversation_id]) + "all: " + str(all_dict[conversation_id]))
            compute_missing_authors(conversation_id, n_count_dict)
        computed_conversations.append(conversation_id)
        print(str(len(computed_conversations)) + " of " + str(len(all_dict)) + " conversations are fully calculated!")
