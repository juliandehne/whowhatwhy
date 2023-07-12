"""
The idea of this script is to download the current state of the conversations that were
intervened in the mturk study.
"""
from mt_study.models import Intervention
from delab.corpus.download_conversations_proxy import download_conversations_by_id


def run():
    interventions = Intervention.objects.filter(sent=True).all()
    conversation_ids = []
    for intervention in interventions:
        conversation_id = intervention.flow.conversation_id
        conversation_ids.append(conversation_id)
    # print(conversation_ids)
    download_conversations_by_id(conversation_ids)
