from delab.models import ConversationFlow


def run():
    flows = ConversationFlow.objects.all()
    for flow in flows:
        assert flow.tweets.count() > 0
        for tweet in flow.tweets.all():
            print(tweet.text)
            print("\n")
        break
