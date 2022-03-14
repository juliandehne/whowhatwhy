from pathlib import Path

import yaml
from googleapiclient import discovery
import os
import json


def run():
    settings_dir = os.path.dirname(__file__)
    project_root = Path(os.path.dirname(settings_dir)).absolute()
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

    analyze_request = {
        'comment': {'text': 'I fricken hate you people'},
        'requestedAttributes': {'TOXICITY': {}}
    }

    response = client.comments().analyze(body=analyze_request).execute()
    print(json.dumps(response, indent=2))
