import logging
import os

from django_pandas.io import read_frame

from delab.models import ConversationFlow, Tweet
from django_project import settings
from delab.corpus.filter_sequences import compute_conversation_flows


def update_flow_picture(simple_request_id=-1):
    """
    computes sentiment flow plots for the conversations
    :param simple_request_id:
    :return:
    """
    conversation_ids = Tweet.objects.filter(simple_request_id=simple_request_id).distinct(
        "conversation_id").values_list("conversation_id",
                                       flat=True).all()
    for conversation_id in conversation_ids:
        compute_conversation_flows(conversation_id)
        compute_flow_matrix(conversation_id)


def compute_flow_matrix(conversation_id):
    """
    because of performance reasons, we are only computing the flow_picture for the longest flow
    """
    flow = ConversationFlow.objects.filter(conversation_id=conversation_id, longest=True).get()
    df = read_frame(flow.tweets.all(), fieldnames=["id",
                                                   "conversation_id",
                                                   "sentiment",
                                                   "sentiment_value",
                                                   "created_at",
                                                   ])
    compute_flow_picture(flow.flow_name, df)


def compute_flow_picture(flow_name, df):
    df_subset = df.sort_values(by=['created_at'])
    df_subset.reset_index(drop=True, inplace=True)
    rolling_column = df_subset['sentiment_value'].rolling(3).mean()
    df_subset = df_subset.assign(rolling_sentiment=rolling_column)
    plot = df_subset.plot(y=['rolling_sentiment', 'sentiment_value'], use_index=True)

    image_path = os.path.join(ConversationFlow.image.field.upload_to, str(flow_name) + ".jpg")
    download_path = os.path.join(settings.MEDIA_ROOT, image_path)
    logging.debug("saving the conversation_flow_pic to {}".format(download_path))
    # plot.figure.show()
    # plot.figure.close()
    if os.path.isfile(download_path):
        os.remove(download_path)
    plot.figure.savefig(download_path, format="jpg")

    flow = ConversationFlow.objects.filter(flow_name=flow_name).get()
    flow.image = image_path
    flow.save(update_fields=["image"])
