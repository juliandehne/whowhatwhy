import logging
import time
from pathlib import Path
import yaml
from googleapiclient import discovery
import os

from delab.models import Tweet

"""
This is the implementation of the perspectives API

"""

logger = logging.getLogger(__name__)


def get_client():
    settings_dir = os.path.dirname(__file__)
    project_root = Path(os.path.dirname(settings_dir)).absolute().parent
    keys_path = os.path.join(project_root, 'twitter/secret/keys_simple.yaml')
    # filename = "C:\\Users\\julia\\PycharmProjects\\djangoProject\\twitter\\secret\\keys_simple.yaml"
    filename = keys_path
    # API_KEY = os.environ.get("gcloud_delab")

    with open(filename) as f:
        my_dict = yaml.safe_load(f)
        API_KEY = my_dict.get("gcloud_delab")

    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        cache_discovery=False
    )
    return client


def compute_toxicity_for_text():
    tweets = Tweet.objects.filter(toxic_value__isnull=True).all()
    for tweet in tweets:
        toxicity = get_toxicity(tweet.text)
        tweet.toxic_value = toxicity
        tweet.is_toxic = toxicity > 0.8
        tweet.save(update_fields=["toxic_value", "is_toxic"])


def get_toxicity(text):
    toxicity = 0
    client = get_client()
    if len(text) > 1:
        try:
            analyze_request = {
                'comment': {
                    'text': text},
                'requestedAttributes': {'SEVERE_TOXICITY': {}}
            }
            response = client.comments().analyze(body=analyze_request).execute()
            if 'status_code' in response and response["status_code"] == 429:
                time.sleep(60)
            toxicity = response["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
            time.sleep(2)
        except Exception as ex:
            logger.error(ex)
    return toxicity
