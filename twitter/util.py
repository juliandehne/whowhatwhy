from requests_oauthlib import OAuth1Session, OAuth2Session
import os
import json
import yaml
import io
import requests
from pathlib import Path


class TwitterConnector:

    def __init__(self, instance_number=2):
        self.lines = None
        self.instance_number = instance_number

    def get_from_twitter(self, search_url, params, is_oauth2=False):
        # Tweet fields are adjustable.
        # Options include:
        # attachments, author_id, context_annotations,
        # conversation_id, created_at, entities, geo, id,
        # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
        # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
        # source, text, and withheld

        # request_token_url = "https://api.twitter.com/oauth/request_token"
        # oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        if is_oauth2:
            headers = self.create_headers()
            json_response = self.__connect_to_endpoint(search_url, headers, params)
            return json_response
        else:
            # Make the request
            oauth = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret,
            )
            try:

                response = oauth.get(search_url, params=params)

                if response.status_code != 200:
                    raise Exception(
                        "Request returned an error: {} {}".format(response.status_code, response.text)
                    )

                print("Response code: {}".format(response.status_code))
                json_response = response.json()

            except ValueError:
                print(
                    "There may have been an issue with the consumer_key or consumer_secret you entered."
                )
            return json_response

    @staticmethod
    def get_secret():
        settings_dir = os.path.dirname(__file__)
        project_root = Path(os.path.dirname(settings_dir)).absolute()
        keys_path = os.path.join(project_root, 'twitter\\secret\\keys_simple.yaml')
        # filename = "C:\\Users\\julia\\PycharmProjects\\djangoProject\\twitter\\secret\\keys_simple.yaml"
        filename = keys_path
        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get("CONSUMER_SECRET")
        # access_token = ""
        # access_token_secret = ""
        # bearer_token = ""
        with open(filename) as f:
            my_dict = yaml.safe_load(f)
            if consumer_key != "":
                consumer_key = my_dict.get("consumer_key")
            if consumer_secret != "":
                consumer_secret = my_dict.get("consumer_secret")
            access_token = my_dict.get("access_token")
            access_token_secret = my_dict.get("access_token_secret")
            bearer_token = my_dict.get("bearer_token")
        return access_token, access_token_secret, bearer_token, consumer_key, consumer_secret

    def create_headers(self):
        access_token, access_token_secret, bearer_token, consumer_key, consumer_secret = self.get_secret()
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    @staticmethod
    def __connect_to_endpoint(search_url, headers, params):
        response = requests.request("GET", search_url, headers=headers, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

