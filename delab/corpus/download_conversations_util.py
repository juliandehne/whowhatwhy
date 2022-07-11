from delab.models import SimpleRequest, TwTopic


def set_up_topic_and_simple_request(query_string, request_id, topic_string):
    # create the topic and save it to the db
    topic, created = TwTopic.objects.get_or_create(
        title=topic_string
    )
    # save the request to the db in order to link the results in the view to the hashtags entered
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
