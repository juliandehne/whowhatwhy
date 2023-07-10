from delab.models import ConversationFlow
from mt_study.models import Classification


def needs_moderation(flow: ConversationFlow):
    classifications = flow.classification_set
    # just take first classification

    if classifications is None or classifications.count() == 0:
        return False

    c = classifications.first()

    return c.needs_moderation is not None and c.is_valid_conversation


def needs_moderation_implicit(flow: ConversationFlow):
    """
    TODO: show if the questions correlate with the strategy needed
    @param flow:
    @return:
    """
    classifications = flow.classification_set

    if classifications is None or classifications.count() == 0:
        return False

    c = classifications.first()

    positive_requirements = c.is_conversation_0 and c.is_conversation_1 and c.is_conversation_2
    one_of_requirements = c.is_conversation_3 or c.is_conversation_4 or c.is_conversation_5 \
                          or c.agenda_control_1 or c.agenda_control_2 or c.agenda_control_3 \
                          or c.emotion_control_1 or c.emotion_control_2 or c.emotion_control_3 \
                          or c.participation_1 or not (c.participation_2) or not c.participation_3 \
                          or c.consensus_seeking_1 or not c.consensus_seeking_2 or c.consensus_seeking_3
    return positive_requirements and one_of_requirements
