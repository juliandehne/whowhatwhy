from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_conversation_trees import get_well_structured_conversation_ids, compute_conversation_properties


def run():
    conversation_ids = get_all_conversation_ids()
    compute_conversation_properties(conversation_ids)
    print("computed the conversation_properties")
    conversation_ids = get_well_structured_conversation_ids()
    print(conversation_ids[:3])