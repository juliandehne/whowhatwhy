from delab.corpus.download_conversations_proxy import download_conversations
from delab.delab_enums import LANGUAGE, PLATFORM

""" This is a django runscript, it can be started in the django home directory with
    $ python manage.py runscript [filename_no_ending]    
"""


def run():
    download_conversations('Klimawandel', "Klimawandel",
                           language=LANGUAGE.GERMAN, platform=PLATFORM.MASTODON)
    download_conversations('Klimawandel', "climatechange",
                           language=LANGUAGE.ENGLISH, platform=PLATFORM.MASTODON)