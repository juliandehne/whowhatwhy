import yaml
from yaml.loader import SafeLoader

from delab.corpus.download_conversations_proxy import download_conversations
from delab.delab_enums import LANGUAGE, PLATFORM
from delab.models import ClimateAuthor

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""

CLIMATE_AUTHOR_PROJECT = 'clima_strat_comm_author_project'


def run():
    words_en = ["climate change", "climate justice",
                "climate activism", "climate activist",
                "global warming", "greenhouse effect",
                "air pollution", "emissions"]

    words_de = ["Klimawandel", "Klimagerechtigkeit", "Klimaktivismus",
                "Klimaaktivist", "Erderwärmung",
                "Klimakatastrophe", "Umweltverschmutzung",
                "Luftverschmutzung", "Zwei Grad Ziel",
                "Treibhauseffekt", "Emissionen"]

    words_de_unclear = ["Nachhaltigkeit", "Luftqualität", "Biodiversität"]
    words_en_unclear = ["sustainability", "air qualitiy", "pollution", "biodiversity"]
    authors = ClimateAuthor.objects.all()
    for author in authors:
        lang = LANGUAGE.ENGLISH
        if author.language == 'de':
            lang = LANGUAGE.GERMAN
            for word in words_de:
                download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                       query_string="(\"" + word + "\" ) from:" + author.twitter_account,
                                       language=lang)
            for word in words_de_unclear:
                download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                       query_string="(\"" + word + "\" Klima) from:" + author.twitter_account,
                                       language=lang)
        else:
            for word in words_en:
                download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                       query_string="(\"" + word + "\" ) from:" + author.twitter_account,
                                       language=lang)
            for word in words_en_unclear:
                download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                       query_string="(\"" + word + "\" climate) from:" + author.twitter_account,
                                       language=lang)
