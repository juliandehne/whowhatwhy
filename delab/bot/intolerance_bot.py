import random

from delab.bot.intolerance_strategies_texts import *
from delab.bot.sender import send_generated_tweet
from delab.delab_enums import LANGUAGE
from delab.models import TWCandidateIntolerance
from delab.toxicity.perspectives import get_toxicity


def generate_answers(candidate):
    text = candidate.tweet.text
    language = candidate.tweet.language
    toxicity = get_toxicity(text)
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
        strategy1 = strategies_de[0]
        strategy2 = strategies_de[1]
        strategy3 = strategies_de[2]
    else:
        if language == LANGUAGE.ENGLISH:
            verbs = verbs_en
            feelings = feelings_en
            group_mapping = group_en_mapping
            strategy1 = strategies_en[0]
            strategy2 = strategies_en[1]
            strategy3 = strategies_en[2]

    group = candidate.political_correct_word
    if group is None:
        if candidate.dict_category is not None:
            group = group_mapping[candidate.dict_category]
        else:
            if language == LANGUAGE.GERMAN:
                group = "Menschen dieser Art"
            else:
                if language == LANGUAGE.ENGLISH:
                    group = "Humans of this kind"

    verb = verbs[tox_level]
    feeling = feelings[tox_level]

    answer1 = strategy1.format()
    answer2 = strategy2.format(group)
    answer3 = strategy3.format(feeling, group)
    return answer1, answer2, answer3


def send_message(candidate: TWCandidateIntolerance):
    answers = {0: candidate.intoleranceanswer.answer1, 1: candidate.intoleranceanswer.answer2,
               2: candidate.intoleranceanswer.answer3}

    alternatives = [0, 1, 2]
    answer_choice_index = random.choice(alternatives)
    answer = answers[answer_choice_index]
    try:
        response = send_generated_tweet(text=answer, reply_to_id=candidate.tweet.twitter_id)
        candidate.intoleranceanswer.date_success_sent = response.created_at
        candidate.intoleranceanswer.twitter_id = response.id
        candidate.intoleranceanswer.save(update_fields=["date_success_sent", "twitter_id"])
    except Exception:
        pass
