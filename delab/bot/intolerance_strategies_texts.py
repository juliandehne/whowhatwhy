verbs_de = ["hassen", "angreifen", "verurteilen"]
verbs_en = ["hate", "attack", "judge"]

feelings_de = ["hasserfüllt gegen", "wütend auf", "genervt von"]
feelings_en = ["full of hate against" "angry at", "annoyed by"]

group_de_mapping = {"rel": "Menschen anderer Religionen",
                    "eth": "Menschen anderer Ethnien",
                    "sex": "Menschen anderer Sexualität",
                    "bod": "Menschen mit anderen Körperformen",
                    "rac": "Menschen anderer Hautfarbe"}

group_en_mapping = {"rel": "people of other religions",
                    "eth": "people of other ethnicities",
                    "sex": "people of other sexualities",
                    "bod": "people of other body shapes",
                    "rac": "people of other skin color"}

strategies_de = {
    0: "Art. 1 der Allgemeinen Erklärung der Menschenrechte lautet:" \
       " „Alle Menschen sind frei und gleich an Würde und Rechten geboren. " \
       "Sie sind mit Vernunft und Gewissen begabt und sollen einander im Geiste der Brüderlichkeit" \
       " begegnen.“ Das gilt auch für {}. Sie sollten diese nicht pauschal {}, " \
       "sondern sich im Geiste der Brüderlichkeit üben.",

    1: "Sagen Sie, dass alle {} schlechte Mitbürger sind? " \
       "Wenn man daraus eine allgemeine Regel machen würde," \
       " dass es reicht zu einer Gruppe wie den {} zu gehören," \
       " um so beurteilt zu werden, würde unsere plurale Gesellschaft in Hass und Spaltungen versinken." \
       " Das kann auch nicht in Ihrem Interesse sein!",
    2: "Warum sind Sie so {} {}? " \
       "Haben Sie alle ihre Möglichkeiten ausgereizt, ihre Meinung zu {} zu überprüfen," \
       " bevor Sie so eine starke Haltung angenommen haben? " \
       "Wenn Sie sich danach fühlen, schreiben Sie doch, " \
       "warum Sie so zu {} denken. Es interessiert mich, warum das so ist."
}

strategies_en = {
    0: "Article 1 of the Universal Declaration of Human Rights reads." \
       "All human beings are born free and equal in dignity and rights. " \
       "They are endowed with reason and conscience, and shall bear one another in the spirit of brotherhood!" \
       "This also applies to {}. You should not  {} sweepingly, " \
       " but practice the spirit of brotherhood.",
    1: "Are you saying that all {} are bad fellow citizens? " \
       "If you were to make this a general rule." \
       " that it is enough to belong to a group like the {}," \
       " to be judged that way, our plural society would sink into hatred and divisions." \
       " That can't be in your interest either!",
    2: "Why are you so {} {}? " \
       "Have you exhausted all her opportunities to check her opinion on {}" \
       " before you adopted such a strong stance? " \
       "If you feel like it, why don't you write " \
       " why you feel that way about {}. I'm interested in why that is."
}