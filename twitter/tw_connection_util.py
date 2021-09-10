from typing import Callable

from TwitterAPI import TwitterAPI
from requests_oauthlib import OAuth1Session, OAuth2Session
import os
import json
import yaml
import io
import requests
from pathlib import Path
import time

from twitter.magic_http_strings import TWEETS_RULES_URL, TWEETS_SEARCH_All_URL, TWEETS_STREAM_URL

from functools import partial


class TwitterAPIWrapper:

    @staticmethod
    def get_twitter_API():
        access_token, access_token_secret, bearer_token, consumer_key, consumer_secret = TwitterUtil.get_secret()
        api = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret, api_version='2')
        return api


class TwitterUtil:

    @staticmethod
    def get_secret():
        settings_dir = os.path.dirname(__file__)
        project_root = Path(os.path.dirname(settings_dir)).absolute()
        keys_path = os.path.join(project_root, 'twitter/secret/keys_simple.yaml')
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


class TwitterConnector:

    def __init__(self, instance_number=2):
        self.lines = None
        self.instance_number = instance_number

    def get_from_twitter(self, search_url, params, is_oauth2=True):
        if is_oauth2:
            headers = self.create_headers()
            json_response = self.__connect_to_endpoint(search_url, headers, params)
            return json_response
        else:
            # TODO implement other connection methods
            pass

    @staticmethod
    def create_headers():
        access_token, access_token_secret, bearer_token, consumer_key, consumer_secret = TwitterUtil.get_secret()
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    @staticmethod
    def __connect_to_endpoint(search_url, headers, params):
        response = requests.request("GET", search_url, headers=headers, params=params)
        # print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        time.sleep(2)

        return response.json()


class TwitterStreamConnector:
    """ Get twitter data from rule based stream API.
        code adapted from the official example:
        https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Filtered-Stream/filtered_stream.py

        Keyword arguments:
        arg1 -- description
        arg2 -- description
    """

    @staticmethod
    def bearer_oauth(r):
        """
        Method required by bearer token authentication.
        """
        access_token, access_token_secret, bearer_token, consumer_key, consumer_secret = TwitterUtil.get_secret()
        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r

    def get_rules(self):
        response = requests.get(
            TWEETS_RULES_URL, auth=self.bearer_oauth
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        # print(json.dumps(response.json()))
        return response.json()

    def delete_all_rules(self, rules):
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            TWEETS_RULES_URL,
            auth=self.bearer_oauth,
            json=payload
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot delete rules (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        # print(json.dumps(response.json()))

    def set_rules(self, rules):
        """ description.

            Keyword arguments:
            arg1 -- the rules to filter the stream by

            # You can adjust the rules if needed
            sample_rules = [
                {"value": "dog has:images", "tag": "dog pictures"},
                {"value": "cat has:images -grumpy", "tag": "cat pictures"},
            ]
        """

        payload = {"add": rules}
        response = requests.post(
            TWEETS_RULES_URL,
            auth=self.bearer_oauth,
            json=payload,
        )
        if response.status_code != 201:
            raise Exception(
                "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        # print(json.dumps(response.json()))

    def get_stream(self, query_params, callback: Callable = print):
        """ because the stream is ... well ... a stream, a delegate function is needed.

            Keyword arguments:
            query_params -- dictionary with the fields that are wanted from the result set
            callback -- a function that takes a json resultset as the only argument
                        should return FALSE if the connection is not needed anymore
        """
        response = requests.get(
            TWEETS_STREAM_URL, auth=self.bearer_oauth, stream=True, params=query_params
        )
        # print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Cannot get stream (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        for response_line in response.iter_lines():
            if response_line == b'':
                break
            if response_line:
                json_response = json.loads(response_line)
                if json_response is None:
                    break
                should_continue = callback(json_response)
                if not should_continue:
                    break
                # print(json.dumps(json_response, indent=4, sort_keys=True))

    def get_from_twitter(self):
        pass
