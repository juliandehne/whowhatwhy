import logging
import os
from pathlib import Path

import praw
import tweepy
import yaml
from twarc import Twarc2

logger = logging.getLogger(__name__)


class TwitterUtil:

    @staticmethod
    def get_aws_secret():
        settings_dir = os.path.dirname(__file__)
        project_root = Path(os.path.dirname(settings_dir)).absolute()
        keys_path = os.path.join(project_root, 'twitter/secret/keys_simple.yaml')
        # filename = "C:\\Users\\julia\\PycharmProjects\\djangoProject\\twitter\\secret\\keys_simple.yaml"
        filename = keys_path
        aws_secret = os.environ.get("aws_secret")
        aws_key_id = os.environ.get("aws_key_id")

        with open(filename) as f:
            my_dict = yaml.safe_load(f)
            if aws_secret != "":
                aws_secret = my_dict.get("aws_secret")
            if aws_key_id != "":
                aws_key_id = my_dict.get("aws_key_id")
        return aws_secret, aws_key_id

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

    @staticmethod
    def get_bot_secret():
        settings_dir = os.path.dirname(__file__)
        project_root = Path(os.path.dirname(settings_dir)).absolute()
        filename = os.path.join(project_root, 'twitter/secret/keys_bot.yaml')
        with open(filename) as f:
            my_dict = yaml.safe_load(f)
            consumer_key = my_dict.get("consumer_key")
            consumer_secret = my_dict.get("consumer_secret")
            access_token = my_dict.get("access_token")
            access_token_secret = my_dict.get("access_token_secret")
            bearer_token = my_dict.get("bearer_token")

        return access_token, access_token_secret, bearer_token, consumer_key, consumer_secret

    @staticmethod
    def get_reddit_secret():
        settings_dir = os.path.dirname(__file__)
        project_root = Path(os.path.dirname(settings_dir)).absolute()
        keys_path = os.path.join(project_root, 'twitter/secret/keys_simple.yaml')
        # filename = "C:\\Users\\julia\\PycharmProjects\\djangoProject\\twitter\\secret\\keys_simple.yaml"
        filename = keys_path
        reddit_secret = os.environ.get("reddit_secret")
        reddit_script_id = os.environ.get("reddit_script_id")
        reddit_user = os.environ.get("reddit_user_name")
        reddit_password = os.environ.get("reddit_password")

        with open(filename) as f:
            my_dict = yaml.safe_load(f)
            if reddit_secret != "":
                reddit_secret = my_dict.get("reddit_secret")
            if reddit_script_id != "":
                reddit_script_id = my_dict.get("reddit_script_id")
            if reddit_user != "":
                reddit_user = my_dict.get("reddit_user_name")
            if reddit_password != "":
                reddit_password = my_dict.get("reddit_password")
        return reddit_secret, reddit_script_id, reddit_user, reddit_password


class DelabTwarc(Twarc2):
    def __init__(self):
        access_token, access_token_secret, bearer_token, consumer_key, consumer_secret = TwitterUtil.get_secret()
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret, bearer_token)


def get_praw():
    user_agent = "django_script:de.uni-goettingen.delab:v0.0.1 (by u/CalmAsTheSea)"
    reddit_secret, reddit_script_id, reddit_user, reddit_password = TwitterUtil.get_reddit_secret()
    reddit = praw.Reddit(client_id=reddit_script_id,
                         client_secret=reddit_secret,
                         user_agent=user_agent,
                         username=reddit_user,
                         password=reddit_password)
    # reddit = praw.Reddit(client_id=reddit_script_id, client_secret=reddit_secret, user_agent=user_agent)
    return reddit


def send_tweet(text, tweet_id):
    # access_token, access_token_secret, bearer_token, consumer_key, consumer_secret = TwitterUtil.get_bot_secret()
    access_token, access_token_secret, bearer_token, consumer_key, consumer_secret = TwitterUtil.get_secret()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    # Creation of the actual interface, using authentication
    api = tweepy.API(auth)
    response = api.update_status(text, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
    return response
