import json

from delab.corpus.download_conversations_proxy import download_conversations
from delab.delab_enums import LANGUAGE, PLATFORM
from delab.tw_connection_util import TwitterStreamConnector

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""


def run():
    download_conversations('Klimawandel', "Klimawandel OR (Klima Wandel) OR (Erderwärmung)",
                           language=LANGUAGE.GERMAN)
    download_conversations('Klimawandel', "(climate change) OR (earth warming)",
                           language=LANGUAGE.ENGLISH)
    # download_conversations('Klimawandel', "Klimawandel OR (Klima Wandel) OR (Erderwärmung)",
    # language=LANGUAGE.GERMAN, platform=PLATFORM.REDDIT)
    # download_conversations('Klimawandel', "(climate change) OR (earth warming)",
    #    language=LANGUAGE.ENGLISH, platform=PLATFORM.REDDIT)
