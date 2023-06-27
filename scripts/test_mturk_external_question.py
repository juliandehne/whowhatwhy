from delab.delab_enums import LANGUAGE
from delab.nce.test_labeling_constraints import create_conversation


def run():
    example_conversation = create_conversation(LANGUAGE.ENGLISH)
    print(example_conversation.to_string())
