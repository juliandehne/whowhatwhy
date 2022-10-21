from delab.analytics.flow_duos import get_flow_duos
from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_conversation_trees import get_well_structured_conversation_ids, compute_conversation_properties
from delab.corpus.filter_sequences import compute_conversation_flows
from delab.models import Conversation


def run():
    print("STEP 1 computing the conversation properties")
    conversation_ids = get_all_conversation_ids()
    to_compute_conversation_ids = []
    for conversation_id in conversation_ids:
        if conversation_id not in list(Conversation.objects.values_list("conversation_id", flat=True)):
            to_compute_conversation_ids.append(conversation_id)

    print("{}/{} conversation properties have been computed previously!")
    compute_conversation_properties(to_compute_conversation_ids)
    print("computed the conversation_properties")
    conversation_ids = get_well_structured_conversation_ids()
    print(conversation_ids[:3])

    print("STEP 2 computing the conversation flows")
    for conversation_id in conversation_ids:
        compute_conversation_flows(conversation_id)

    print("STEP 3 compute the dual flows")
    dual_flows = get_flow_duos()





