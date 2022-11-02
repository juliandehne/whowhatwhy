from delab.analytics.cccp_analytics import calculate_conversation_author_metrics, compute_all_cccp_authors
from delab.analytics.flow_duos import get_flow_duos
from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_conversation_trees import get_well_structured_conversation_ids, compute_conversation_properties
from delab.corpus.filter_sequences import compute_conversation_flows
from delab.models import Conversation, ConversationFlow
from delab.toxicity.perspectives import compute_toxicity_for_text


def run():
    print("STEP 1 computing the conversation properties")
    conversation_ids = set(get_all_conversation_ids())

    to_compute_conversation_ids = conversation_ids - set(Conversation.objects.values_list("conversation_id", flat=True))

    print("{}/{} conversation properties have been computed previously!")
    compute_conversation_properties(to_compute_conversation_ids)

    print("STEP 2 computing the conversation flows")
    to_compute_conversation_ids_flows = conversation_ids - set(
        ConversationFlow.objects.values_list("conversation_id", flat=True))
    count = 0
    for conversation_id in to_compute_conversation_ids_flows:
        compute_conversation_flows(conversation_id)
        count += 1
        print(" computed flows for {}/{} conversations".format(count, len(to_compute_conversation_ids_flows)))

    print("STEP 3 compute toxicity for tweets")
    compute_toxicity_for_text()

    print("STEP 4 compute the dual flows")
    # dual_flows = get_flow_duos()

    print("STEP 5: calculate conversation author metrics")
    calculate_conversation_author_metrics()

    print("STEP 6: calculate cccp examples")
    # compute_all_cccp_authors()

