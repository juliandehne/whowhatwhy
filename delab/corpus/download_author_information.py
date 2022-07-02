"""
 use this endpoint (also in magic https) GET https://api.twitter.com/2/users/253257813?user.fields=location,username,name
"""
import logging
import time

from django.db import IntegrityError
from django.db.models import Q

from delab.models import Tweet, TweetAuthor
from delab.delab_enums import PLATFORM
from delab.tw_connection_util import DelabTwarc
from util.abusing_lists import batch

logger = logging.getLogger(__name__)


def update_authors(simple_request_id=-1, topic: str = None, platform=PLATFORM.TWITTER):
    """
    downlaod detailed author information for the author's of the tweets
    :param topic: the topic string in the twtopic table
    :param platform:
    :param simple_request_id: (int) for the web-downloader. if it is negative, all authors will be queried
    :return:
    """
    if platform == PLATFORM.REDDIT:
        print("author detail download NOT IMPLEMENTED FOR REDDIT")
    if platform == PLATFORM.TWITTER:
        if simple_request_id < 0:
            if topic is not None:
                author_ids = Tweet.objects.filter(tw_author__isnull=True, topic__title=topic,
                                                  platform=platform).values_list('author_id', flat=True)
            else:
                author_ids = Tweet.objects.filter(tw_author__isnull=True, platform=platform).values_list(
                    'author_id', flat=True)
        else:
            if topic is not None:
                author_ids = Tweet.objects.filter(Q(tw_author__isnull=True) & Q(topic__title=topic)
                                                  & Q(simple_request_id=simple_request_id)
                                                  & Q(platform=platform)).values_list('author_id', flat=True)
            else:
                author_ids = Tweet.objects.filter(Q(tw_author__isnull=True)
                                                  & Q(simple_request_id=simple_request_id)
                                                  & Q(platform=platform)).values_list('author_id', flat=True)
        # create only one connector for quote reasons
        download_authors(author_ids)


def download_authors(author_ids):
    twarc = DelabTwarc()
    new_authors = []
    for author_id in author_ids:

        try:
            author = TweetAuthor.objects.get(twitter_id=author_id)
        except TweetAuthor.DoesNotExist:
            author = None

        if author:
            tweets = Tweet.objects.filter(author_id=author_id).all()
            for tweet in tweets:
                tweet.tw_author = author
                tweet.save(update_fields=["tw_author"])
        else:
            new_authors.append(author_id)
    new_authors = list(set(new_authors))
    author_batches = batch(new_authors, 99)
    for author_batch in author_batches:
        download_user_batch(author_batch, twarc)


def download_user_batch(author_batch, twarc):
    """
    Utility function to download all the author data in a batch using the twitter api existing for that reason
    :param author_batch:
    :param twarc:
    :return:
    """
    users = twarc.user_lookup(users=author_batch)

    for userbatch in users:
        if "data" in userbatch:
            for author_payload in userbatch["data"]:
                # print(author_payload)
                user_obj = author_payload
                try:
                    author_id = user_obj["id"]
                    tweets = Tweet.objects.filter(author_id=author_id).all()
                    author, created = TweetAuthor.objects.get_or_create(
                        twitter_id=user_obj["id"],
                        name=user_obj["name"],
                        screen_name=user_obj["username"],
                        location=user_obj.get("location", "unknown"),
                        followers_count=user_obj["public_metrics"]["followers_count"],
                        # tweet=tweet
                    )
                    author.full_clean()
                    for tweet in tweets:
                        tweet.tw_author = author
                        tweet.save(update_fields=["tw_author"])

                except IntegrityError:
                    logger.error("author already exists")

                except Exception as e:
                    # traceback.print_exc()
                    logger.info(
                        "############# Exception: Rate limit was exceeded while downloading author info." +
                        " Going to sleep for 15!")
                    time.sleep(15 * 60)
        else:
            if "errors" in userbatch:
                # and userbatch["errors"]["title"] == "Not Found Error"
                author_batch_size = len(author_batch)
                errors = userbatch["errors"]
                for error in errors:
                    if "value" in error:
                        user_not_found = int(error["value"])
                        author_batch.remove(user_not_found)
                        # create stand_in_user
                        tweets = Tweet.objects.filter(author_id=user_not_found).all()
                        author, created = TweetAuthor.objects.get_or_create(
                            twitter_id=user_not_found,
                            name="user_deleted",
                            screen_name="user_deleted",
                            # tweet=tweet
                        )
                        author.full_clean()
                        for tweet in tweets:
                            tweet.tw_author = author
                            tweet.save(update_fields=["tw_author"])
                if len(author_batch) < author_batch_size:
                    download_user_batch(author_batch, twarc)
