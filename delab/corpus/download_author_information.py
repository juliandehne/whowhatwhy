# TODO download the author names, location etc. for the given authors
"""
 use this endpoint (also in magic https) GET https://api.twitter.com/2/users/253257813?user.fields=location,username,name
"""
from django.db import IntegrityError
from django.db.models import Q

from delab.magic_http_strings import USER_URL
from delab.models import Tweet, TweetAuthor
from delab.tw_connection_util import TwitterConnector


def get_author_from_twitter(tweet, connector):
    params = {"user.fields": "name,username,location,public_metrics"}

    json_result = connector.get_from_twitter(USER_URL.format(tweet.author_id), params, True)
    # logger.info(json.dumps(json_result, indent=4, sort_keys=True))
    return json_result


def update_authors():
    tweets = Tweet.objects.filter(Q(tw_author__isnull=True)).all()
    # create only one connector for quote reasons
    connector = TwitterConnector(1)
    try:
        for tweet in tweets:
            author_payload = get_author_from_twitter(tweet, connector=connector)
            # print(author_payload)
            if "data" in author_payload:
                author = TweetAuthor(
                    twitter_id=author_payload["data"]["id"],
                    name=author_payload["data"]["name"],
                    screen_name=author_payload["data"]["username"],
                    location=author_payload["data"].get("location", "unknown"),
                    followers_count=author_payload["data"]["public_metrics"]["followers_count"],
                    tweet=tweet
                )
                author.save()
    except IntegrityError:
        print("author already exists")
