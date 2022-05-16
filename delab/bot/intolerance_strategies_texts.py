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
       "Sie sind mit Vernunft und Gewissen begabt und sollen einander im Geiste der Brüderlichkeit\"",
    1: "Wäre es eine allgemeine Regel, dass Menschen so beurteilt werden, "
       "nur weil sie einer Gruppe wie den {} angehören, "
       "würde unsere plurale Gesellschaft in Hass und Spaltung versinken.",
    2: "Warum sind Sie so {} {}? "}


strategies_en = {
    0: "Article 1 of the Universal Declaration of Human Rights reads." \
       "All human beings are born free and equal in dignity and rights. " \
       "They are endowed with reason and conscience, and ought to treat one another in a spirit of brotherhood.\"",
    1: "Were it a general rule that men should be so judged, " \
       "just because they belong to a group like the {}, " \
       "our plural society would sink into hatred and division.", \
    2: "Why are you so {} {}? "}
