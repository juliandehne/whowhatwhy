import io
import zipfile

from delab.analytics.flow_duos import get_flow_duo_windows
from delab.corpus.filter_sequences import get_conversation_flows, compute_conversation_flows
from delab.models import ConversationFlow
from django.http import HttpResponse


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


def render_duo_flows():
    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')
    filename = "duo_flows_conversations.zip"

    windows = get_flow_duo_windows()
    for window in windows:
        zip_file.writestr("conversation__duo_flow_{}_{}.txt".format(window.name1, window.name2), window.to_str())

    zip_file.close()
    # Return zip
    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    return response

