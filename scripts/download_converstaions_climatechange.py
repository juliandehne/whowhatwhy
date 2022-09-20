import json
import yaml
from yaml.loader import SafeLoader

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
    download_conversations('Klimawandel', "Klimawandel OR (Klima Wandel) OR (Erderwärmung)",
                           language=LANGUAGE.GERMAN, platform=PLATFORM.REDDIT)
    download_conversations('Klimawandel', "(climate change) OR (earth warming)",
                           language=LANGUAGE.ENGLISH, platform=PLATFORM.REDDIT),
    download_conversations('Klimawandel', read_yaml('ger'),
                           language=LANGUAGE.GERMAN, platform=PLATFORM.TWITTER)
    download_conversations('KLimawandel', read_yaml('en'),
                           language=LANGUAGE.ENGLISH, platform=PLATFORM.TWITTER)


def read_yaml(lang):
    if lang == 'ger':
        with open('twitter/strategic_communication/climate_change.yaml') as file:
            data = yaml.load(file, Loader=SafeLoader)
    else:
        with open('twitter/strategic_communication/climate_change_en.yaml') as file:
            data = yaml.load(file, Loader=SafeLoader)
    accounts = ""
    for key in data:
        data2 = data[key]
        for key2 in data2:
            for key3 in key2:
                values = list(key2[key3].values())
                accounts += "from:" + (values[1]) + " OR "
    return accounts[:-4]
