import csv
from functools import partial

from requests import HTTPError

from delab.corpus.download_conversations_proxy import download_conversations
from delab.delab_enums import LANGUAGE, PLATFORM
from delab.models import Tweet, ModerationCandidate2, TwTopic, SimpleRequest
from util.abusing_lists import batch

MODTOPIC2 = "moderationdictmining"


def download_mod_tweets(recent=True, platform=PLATFORM.TWITTER):
    for lang in LANGUAGE:
        with open("delab/mm/FunctionPhrases.csv") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            next(reader, None)  # skip the headers
            download_mod_tweets_for_language(reader, lang, recent, platform)


def tweet_filter(query: str, tweet: Tweet):
    """
    this asserts that the tweet will be automatically linked to the candidate and the simple request containing the query for later analysis
    :param query:
    :param tweet:
    :return:
    """

    # create the topic and save it to the db
    topic, created = TwTopic.objects.get_or_create(
        title=MODTOPIC2
    )
    simple_request, created2 = SimpleRequest.objects.get_or_create(
        title=query,
        topic=topic
    )
    tweet.simple_request = simple_request
    # tweet.topic = topic
    if Tweet.objects.filter(twitter_id=tweet.twitter_id).exists():
        tweet = Tweet.objects.filter(twitter_id=tweet.twitter_id).first()
    else:
        tweet.save()

        contained = test_tweet_matches_dict(query, tweet)
        if contained:
            ModerationCandidate2.objects.get_or_create(
                tweet=tweet
            )
    return tweet


def test_tweet_matches_dict(query, tweet):
    """
    because the whole conversation is always being downloaded the references to which was the original candidate
    was lost. For this reason the text is checked for containment of the keywords of the query.
    The is a low probability this will produce additional candidates.
    :param query:
    :param tweet:
    :return:
    """
    contained = True
    if "is:reply" in query:
        index_original_query_end = query.index("is:reply")
        query = query[:index_original_query_end]
    keywords = query.replace("(", "").replace(")", "").replace("-", "").replace("\"", "")
    for item in keywords.split(" "):
        if item in tweet.text:
            contained = contained and True
        else:
            contained = False
    return contained


def download_mod_tweets_for_language(reader, lang, recent, platform):
    """
    This function extracts the phrases from the csv sheet
    :param platform:
    :param reader:
    :param lang:
    :param recent:
    :return:
    """
    for row in reader:
        if lang == LANGUAGE.ENGLISH:
            queries = row[8]
            download_mod_helper(lang, queries, recent, add_pol_contexts=False, platform=platform)
        else:
            if lang == LANGUAGE.GERMAN:
                queries = row[9]
                download_mod_helper(lang, queries, recent, add_pol_contexts=False, platform=platform)


def generate_contexts():
    # interesting poltical contexts from  https://raw.githubusercontent.com/twitterdev/twitter-context-annotations/main/files/evergreen-context-entities-20220601.csv

    # political issues, political talk, politics europe, political news
    # contexts = ["131.840159122012102656", "131.1488973753274929152", "131.847878884917886977",
    #             "131.1281313284952485889", "22.1281313284952485889", "3.10027336130"]
    contexts = []
    with open("delab/mm/evergreen-context-entities-20220601.csv") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        next(reader, None)  # skip the headers
        for row in reader:
            if "politi" in row[2] or "polic" in row[2].lower():
                if "," in row[0]:
                    for domain in row[0].replace("\"", "").split(","):
                        contexts.append(domain + "." + row[1])
                else:
                    contexts.append(row[0] + "." + row[1])

    return contexts


def download_mod_helper(lang, queries, recent, platform, add_pol_contexts=False):
    """
    A helper function to further extract the phrases from the csv
    :param platform:
    :param add_pol_contexts:
    :param lang:
    :param queries:
    :param recent:
    :return:
    """

    contexts_full = generate_contexts()
    batch_size = 4
    n = len(contexts_full)
    rest = n % 4
    contexts_full = contexts_full[:-rest]

    for query in queries.split(";"):
        if query.strip() != "":
            # query = ast.literal_eval(query)
            query2 = query.replace("'", "\"")

            if add_pol_contexts:
                for contexts_batch in batch(contexts_full, batch_size):
                    if len(contexts_batch) == batch_size:
                        pol_contexts = "(context:{} OR ".format(contexts_batch[0])
                        for elem in contexts_batch[1:-1]:
                            pol_contexts = pol_contexts + "context:{} OR ".format(elem)
                        pol_contexts = pol_contexts + "context:{})".format(contexts_batch[-1])

                        query_string = query2 + " is:reply " + pol_contexts
                        moderation_tweet_filter = partial(tweet_filter, query_string)
                        try:
                            download_conversations(topic_string=MODTOPIC2, query_string=query_string, language=lang,
                                                   tweet_filter=moderation_tweet_filter,
                                                   recent=recent)
                        except HTTPError as ex:
                            print("error in query {}".format(ex))
            else:
                query_string = query2
                if platform == PLATFORM.TWITTER:
                    query_string = query2 + " is:reply "
                moderation_tweet_filter = partial(tweet_filter, query_string)
                try:
                    download_conversations(topic_string=MODTOPIC2, query_string=query_string, language=lang,
                                           tweet_filter=moderation_tweet_filter,
                                           recent=recent, platform=platform)
                except HTTPError as ex:
                    print("error in query {}".format(ex))
