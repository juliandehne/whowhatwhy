import re
from time import sleep

import spacy

from delab.models import TWCandidateIntolerance, LANGUAGE
from delab.toxicity.perspectives import get_client


def get_toxicity_from_perspective(text):
    try:
        analyze_request = {
            'comment': {
                'text': text},
            'requestedAttributes': {'SEVERE_TOXICITY': {}}
        }

        client = get_client()
        response = client.comments().analyze(body=analyze_request).execute()
        toxicity = response["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
        return toxicity
    except Exception:
        print("something went wrong")


def generate_answers(candidate):
    text = candidate.tweet.text
    language = candidate.tweet.language
    toxicity = get_toxicity_from_perspective(text)
    # bound to the array indixes. The more toxic words come left in the array
    tox_level = 2
    if toxicity > 0.8:
        tox_level = 0
    if toxicity > 0.6:
        tox_level = 1
    if language == LANGUAGE.GERMAN:
        verbs = verbs_de
        feelings = feelings_de
        group_mapping = group_de_mapping
        strategy1 = strategy1_de
        strategy2 = strategy2_de
        strategy3 = strategy3_de

    group = candidate.political_correct_word
    if group is None:
        if candidate.dict_category is not None:
            group = group_mapping[candidate.dict_category]
        else:
            group = "Menschen dieser Art"

    verb = verbs[tox_level]
    feeling = feelings[tox_level]

    answer1 = strategy1.format(group, verb)
    answer2 = strategy2.format(group, group)
    answer3 = strategy3.format(feeling, group, group, group)
    return answer1, answer2, answer3


verbs_de = ["hassen", "angreifen", "verurteilen"]
verbs_en = ["hate", "attack", "judge"]

feelings_de = ["hasserfüllt gegen", "wütend auf", "genervt von"]
feelings_en = ["full of hate against" "angry at", "annoyed by"]

group_de_mapping = {"rel": "Menschen anderer Religionen",
                    "eth": "Menschen anderer Ethnien",
                    "sex": "Menschen anderer Sexualität",
                    "bod": "Menschen mit anderen Körperformen",
                    "rac": "Menschen anderer Hautfarbe"}

strategy1_de = "Art. 1 der Allgemeinen Erklärung der Menschenrechte lautet:" \
               " „Alle Menschen sind frei und gleich an Würde und Rechten geboren. " \
               "Sie sind mit Vernunft und Gewissen begabt und sollen einander im Geiste der Brüderlichkeit" \
               " begegnen.“ Das gilt auch für {}. Sie sollten diese nicht pauschal {}, " \
               "sondern sich im Geiste der Brüderlichkeit üben."

strategy2_de = "Sagen Sie, dass alle {} schlechte Mitbürger sind? " \
               "Wenn man daraus eine allgemeine Regel machen würde," \
               " dass es reicht zu einer Gruppe wie den {} zu gehören," \
               " um so beurteilt zu werden, würde unsere plurale Gesellschaft in Hass und Spaltungen versinken." \
               " Das kann auch nicht in ihrem Interesse sein!"

strategy3_de = "Warum sind Sie so {} {}? " \
               "Haben Sie alle ihre Möglichkeiten ausgereizt, ihre Meinung zu {} zu überprüfen," \
               " bevor Sie so eine starke Haltung angenommen haben? " \
               "Wenn Sie sich danach fühlen, schreiben Sie doch, " \
               "warum Sie so zu {} denken. Es interessiert mich, warum das so ist."
