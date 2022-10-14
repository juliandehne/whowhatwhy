from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_sequences import get_conversation_flows, compute_conversation_flows
from delab.models import ConversationFlow
from django.db.utils import IntegrityError


def run():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        compute_conversation_flows(conversation_id)



