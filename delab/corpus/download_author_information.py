"""
 use this endpoint (also in magic https) GET https://api.twitter.com/2/users/253257813?user.fields=location,username,name
"""
import logging
import time

from django.db import IntegrityError
from django.db.models import Q

from delab.delab_enums import PLATFORM, CLIMATEAUTHOR
from delab.models import Tweet, TweetAuthor, ClimateAuthor
from delab.tw_connection_util import DelabTwarc
from util.abusing_lists import batch

logger = logging.getLogger(__name__)


def update_authors(simple_request_id=-1, topic: str = None, platform=PLATFORM.TWITTER):
    """
    Download detailed author information for the author's of the tweets
    This creates rows in the author table with the full name instead of only the id in the tweet table
    :param topic: the topic title string in the twtopic table
    :param platform:
    :param simple_request_id: (int) for the web-downloader. if it is negative, all authors will be queried
    :return:
    """
    if platform == PLATFORM.REDDIT:
        print("author detail download NOT IMPLEMENTED FOR REDDIT")
    if platform == PLATFORM.TWITTER:
        if simple_request_id < 0:
            """
                Get the id of all authors were the tweet was downloaded but the author not
            """
            if topic is not None:
                # only download those authors with given topic and which have not been downloaded before (not null)
                author_ids = Tweet.objects.filter(tw_author__isnull=True, topic__title=topic,
                                                  platform=platform).values_list('author_id', flat=True)
            else:
                # download all topics no matter which topic
                author_ids = Tweet.objects.filter(tw_author__isnull=True, platform=platform).values_list(
                    'author_id', flat=True)
        else:
            # same as before but with the given request id (used for downloads using the website instead of
            # a django script
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
    new_authors = repair_fk_tweet_authors(author_ids)
    # batch processing means breaking down a big loop
    # in smaller loops
    author_batches = batch(new_authors, 99)
    for author_batch in author_batches:
        download_user_batch(author_batch, twarc)


def repair_fk_tweet_authors(author_ids):
    """
         Historically tweets and authors were not linked by foreign key
         This creates the foreign key association.
         In fact, it may be worth testing if this method is still needed. It looks obsolete!!
         @param author_ids: the list of ids that need to be downloaded
         @return:the list were authors are appended to, that are not yet in the author table
    """
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
    return new_authors


def download_user_batch(author_batch, twarc):
    """
    Utility function to download all the author data in a batch (in chunks) using the twitter api existing for that reason
    :param author_batch:
    :param twarc:
    :return:
    """
    # downloads the author data like names
    users = twarc.user_lookup(users=author_batch)

    for user_batch in users:
        if "data" in user_batch:
            # iterate through the author data
            for author_payload in user_batch["data"]:
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

                # except Exception as e:
                # Normally the API does this, too
                # This kind of error handling is very dangerous and thus commented out
                # traceback.print_exc()
                #    logger.info(
                #        "############# Exception: Rate limit was exceeded while downloading author info." +
                #        " Going to sleep for 15!")
                #    time.sleep(15 * 60)
        else:
            if "errors" in user_batch:
                deal_with_missing_authors(author_batch, twarc, user_batch)


def deal_with_missing_authors(author_batch, twarc, userbatch):
    """
    create fake users for those that could not be downloaded
    """
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


def create_climate_authors(data):
    accounts = []
    for key in data:
        data2 = data[key]
        for key2 in data2:
            k = list(key2.keys())
            type = k[0]
            for key3 in key2:
                author = key2[key3]
                name = author['name']
                twitter_account = author['twitter_account']
                governmental = False
                if 'governmental' in author.keys():
                    if author['governmental'] == 'true':
                        governmental = True
                elif type == 'politician':
                    governmental = True
                if name == "":
                    continue
                climate_author = ClimateAuthor(type=type, name=name, twitter_account=twitter_account, governmental=governmental)
                climate_author.save()
                accounts.append(twitter_account)
    #update_is_climate_author(accounts)
    #set_climate_author_type()


def update_is_climate_author(names):
    twarc = DelabTwarc()
    ids = twarc.user_lookup(users=names, usernames=True)
    missing_authors = []
    missing_author_names = []
    for id_batch in ids:
        if "data" in id_batch:
            for author_payload in id_batch["data"]:
                tw_id = author_payload["id"]
                tw_username = author_payload["username"]
                climate_authors = TweetAuthor.objects.filter(twitter_id=tw_id).all()
                if climate_authors.count() == 0:
                    missing_authors.append(tw_id)
                    missing_author_names.append(tw_username)
                for tweetAuthor in climate_authors:
                    tweetAuthor.is_climate_author = True
                    tweetAuthor.save(update_fields=["is_climate_author"])
                download_authors(missing_authors)
                update_is_climate_author(missing_author_names)


def set_climate_author_type():
    climate_authors = TweetAuthor.objects.filter(is_climate_author=True).all()
    for author in climate_authors:
        author_name = author.name
        cl_author = ClimateAuthor.objects.filter(name=author_name)
        author_type = cl_author.type
        if author_type == 'organisation' and cl_author.governmental():
            author.climate_author_type = CLIMATEAUTHOR.NGO
            author.save()
        else:
            author.climate_author_type = author_type
            author.save()
