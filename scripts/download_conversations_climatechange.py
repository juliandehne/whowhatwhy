import yaml
from yaml.loader import SafeLoader

from delab.corpus.download_conversations_proxy import download_conversations
from delab.delab_enums import LANGUAGE, PLATFORM

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""

CLIMATE_AUTHOR_PROJECT = 'clima_strat_comm_author_project'


def run():
    # download_conversations('Klimawandel',read_yaml('ger'),
    #                      language=LANGUAGE.GERMAN, platform= PLATFORM.TWITTER)
    download_conversations(CLIMATE_AUTHOR_PROJECT, read_yaml('en'), language=LANGUAGE.ENGLISH,
                           platform=PLATFORM.TWITTER)


def read_yaml(lang):
    if lang == 'ger':
        with open('twitter/strategic_communication/climate_change.yaml') as file:
            data = yaml.load(file, Loader=SafeLoader)
            accounts = "Klimawandel ("
    else:
        with open('twitter/strategic_communication/climate_change_en.yaml') as file:
            data = yaml.load(file, Loader=SafeLoader)
            accounts = "\"climate change\" ("
    for key in data:
        data2 = data[key]
        for key2 in data2:
            for key3 in key2:
                values = list(key2[key3].values())
                account_name = (values[1])
                if account_name is not None and len(account_name) > 0:
                    accounts += "from:" + account_name + " OR "
    return accounts[:-4] + ")"
