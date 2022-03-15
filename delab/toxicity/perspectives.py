from pathlib import Path

import yaml
from googleapiclient import discovery
import os


def get_client():
    settings_dir = os.path.dirname(__file__)
    project_root = Path(os.path.dirname(settings_dir)).absolute().parent
    keys_path = os.path.join(project_root, 'twitter/secret/keys_simple.yaml')
    # filename = "C:\\Users\\julia\\PycharmProjects\\djangoProject\\twitter\\secret\\keys_simple.yaml"
    filename = keys_path
    API_KEY = os.environ.get("gcloud_delab")

    with open(filename) as f:
        my_dict = yaml.safe_load(f)
        if API_KEY != "":
            API_KEY = my_dict.get("gcloud_delab")

    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        cache_discovery=False
    )
    return client


class UkraineComment:
    def __init__(self, text, language, conversation_id, platform):
        self.toxicity_value = 0
        self.text = text
        self.language = language
        self.conversation_id = conversation_id
        self.platform = platform

    def set_toxicity(self, toxicity):
        self.toxicity_value = toxicity
