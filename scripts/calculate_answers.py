import re

import spacy

from delab.bot.intolerance_bot import generate_answers
from delab.models import TWCandidateIntolerance
from delab.delab_enums import LANGUAGE
from delab.toxicity.perspectives import get_client

NER = spacy.load("en_core_web_lg")


def run():
    candidates = TWCandidateIntolerance.objects.filter(twintolerancerating__u_clearness_rating=2,
                                                       twintolerancerating__u_person_hate=False,
                                                       twintolerancerating__u_intolerance_rating=2,
                                                       tweet__language=LANGUAGE.GERMAN)
    for candidate in candidates:
        answer1, answer2, answer3 = generate_answers(candidate)
        print(answer1)
        print("\n")
        print(answer2)
        print("\n")
        print(answer3)


def get_named_entities(temp):
    temp = re.sub("@[A-Za-z0-9_]+", "", temp)
    temp = re.sub("#[A-Za-z0-9_]+", "", temp)
    # removing links
    temp = re.sub(r"http\S+", "", temp)
    temp = re.sub(r"www.\S+", "", temp)
    # removing punctuation
    # temp = re.sub('[()!?]', ' ', temp)
    # temp = re.sub("\[.*?\]", ' ', temp)
    # alphanumeric
    # temp = re.sub("[^a-z0-9A-ZäöüÄÖÜ]", " ", temp)
    # temp = re.sub("RT", "", temp)
    text = temp.strip()
    print(text)
    text1 = NER(text)
    for word in text1.ents:
       print(word.text, word.label_)
    return text


