from delab.models import SimpleRequest, TwTopic


def set_up_topic_and_simple_request(query_string, request_id, topic_string):
    # save the request to the db in order to link the results in the view to the hashtags entered
    if SimpleRequest.objects.filter(title=query_string).exists():
        simple_request = SimpleRequest.objects.filter(title=query_string).get()
        topic = simple_request.topic
    else:
        # create the topic and save it to the db
        topic, created = TwTopic.objects.get_or_create(
            title=topic_string
        )
        if request_id > 0:
            simple_request, created = SimpleRequest.objects.get_or_create(
                pk=request_id,
                topic=topic
            )
        else:
            # request_string = "#" + ' #'.join(hashtags)
            simple_request, created = SimpleRequest.objects.get_or_create(
                title=query_string,
                topic=topic
            )
    return simple_request, topic


def apply_tweet_filter(tweet, tweet_filter):
    if tweet_filter is not None:
        tweet = tweet_filter(tweet)
        # the idea here is that the filter may have to save the tweet to create foreign keys
        # in this case the save method will fail because of an integrity error
        if tweet.pk is None:
            tweet.save()

    else:
        tweet.save()
