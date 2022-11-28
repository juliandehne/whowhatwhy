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
    authors = ClimateAuthor.objects.all()
    climate_convo = "(\"climate change\" OR Klimawandel) "
    download_conversations(CLIMATE_AUTHOR_PROJECT,"(\"climate change\" OR Klimawandel) from:Perowinger94", language=LANGUAGE.GERMAN)
    #for author in authors:
        #download_conversations(CLIMATE_AUTHOR_PROJECT, climate_convo + "from:" + author.twitter_account, language=author.language)


