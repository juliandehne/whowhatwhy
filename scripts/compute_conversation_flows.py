from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_sequences import get_conversation_flows
from delab.models import ConversationFlow
from django.db.utils import IntegrityError


def run():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        try:
            flows = get_conversation_flows(conversation_id)
            for name, tweets in flows.items():
                flow, created = ConversationFlow.objects.get_or_create(
                    flow_name=name,
                    conversation_id=conversation_id
                )
                flow.tweets.add(*tweets)
        except AssertionError as ae:
            pass

