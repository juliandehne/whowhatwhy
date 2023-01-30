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
    words_en = "(\"climate change\" OR \"climate justice\" OR \"climate activism\" OR \"climate activist\" OR \"global warming\"OR \"greenhouse effect\" OR \"air pollution\" OR \"emissions\" OR \"climate crisis\")"

    words_de = "(Klimawandel OR Klimagerechtigkeit OR Klimaktivismus OR Klimaaktivist OR Erderwärmung OR Klimakatastrophe OR Umweltverschmutzung OR Luftverschmutzung OR \"Zwei Grad Ziel\" OR Treibhauseffekt OR Emissionen OR Klimakrise)"

    words_de_unclear = "(Nachhaltigkeit OR Luftqualität OR Biodiversität) KLima "
    words_en_unclear = "(sustainability OR \"air qualitiy\" OR pollution OR biodiversity) climate "
    authors = ClimateAuthor.objects.all()
    for author in authors:
        lang = LANGUAGE.ENGLISH
        if author.language == 'de':
            lang = LANGUAGE.GERMAN
            download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                   query_string=words_de + "from:" + author.twitter_account,
                                   language=lang)
            download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                   query_string=words_de_unclear + "from:" + author.twitter_account,
                                   language=lang)

        else:
            download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                   query_string= words_en + "from:" + author.twitter_account,
                                   language=lang)
            download_conversations(topic_string=CLIMATE_AUTHOR_PROJECT,
                                   query_string=words_en_unclear + "from:" + author.twitter_account,
                                   language=lang)
