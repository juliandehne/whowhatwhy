import datetime

from pytz.exceptions import AmbiguousTimeError

from delab.models import TweetAuthor, PLATFORM, Timeline
from delab.tw_connection_util import get_praw

from util.abusing_strings import convert_to_hash


def download_timelines(simple_request_id=-1):
    reddit = get_praw()
    if simple_request_id < 0:
        authors = TweetAuthor.objects.filter(platform=PLATFORM.REDDIT, has_timeline__isnull=True).all()
    else:
        authors = TweetAuthor.objects.filter(platform=PLATFORM.REDDIT, tweet__simple_request_id=simple_request_id,
                                             has_timeline__isnull=True).all()

    for author in authors:
        reddit_name = author.name
        redditor2 = reddit.redditor(reddit_name)
        comments = redditor2.comments.new(limit=None)
        for comment in comments:
            # print(comment.body)
            created_time = datetime.datetime.fromtimestamp(comment.created)
            try:
                Timeline.objects.get_or_create(
                    author_id=author.twitter_id,
                    tweet_id=convert_to_hash(comment.id),
                    text=comment.body,
                    lang=comment.subreddit.lang,
                    platform=PLATFORM.REDDIT,
                    conversation_id=convert_to_hash(comment.submission.id),
                    created_at=created_time,
                    tw_author=author
                )
                author.has_timeline = True
            except AmbiguousTimeError:
                print("could not store time to db {}".format(created_time))
            TweetAuthor.objects.bulk_update(authors, fields=["has_timeline"])
