from django.test import TestCase
from blog.models import Post
import logging
from googletrans import Translator
import os
from pathlib import Path
import yaml
import pprint
from django.test.runner import DiscoverRunner


# Create your tests here.
class TwitterSandbox(TestCase):

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass

    def test_google_trans(self):
        example_text = "Herr Präsident, Deutschland heißt sie herzlich willkommen! Deutsche wollen mehr Usbekische Migranten."
        translator = Translator()
        translated = translator.translate(example_text).text
        print("translated text = {}".format(translated))

    def test_yaml_import(self):
        settings_dir = os.path.dirname(__file__)
        project_root = Path(os.path.dirname(settings_dir)).absolute()
        twitter_addresses_yaml = Path.joinpath(project_root, "twitter\\twitter_addresses.yaml")
        with open(twitter_addresses_yaml) as f:
            # use safe_load instead load
            data_map = yaml.safe_load(f)

        class TwitterAddresses:
            def __init__(self, entries):
                self.__dict__.update(entries)

        addresses = TwitterAddresses(data_map)
        pp = pprint.PrettyPrinter(indent=4)
        ##pp.pprint(addresses)

        pp.pprint(addresses.institutions[0])
