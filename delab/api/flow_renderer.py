from delab.corpus.filter_sequences import get_conversation_flows, compute_conversation_flows
from delab.models import ConversationFlow


def render_longest_flow_txt(conversation_id):
    compute_conversation_flows(conversation_id)
    longest_flow = ConversationFlow.objects.filter(longest=True, conversation_id=conversation_id).get()

    sorted_tweets = sorted(longest_flow.tweets.all(), key=lambda x: x.created_at)
    # sorted_tweets = longest_flow.tweets.all()
    result = ""
    for tweet in sorted_tweets:
        if tweet.tw_author is not None:
            author_name = tweet.tw_author.name
        else:
            author_name = tweet.author_id
        result += "{}: ".format(author_name) + tweet.text
        result += "\n\n\n"
    return result
