import io

from django.core.files.images import ImageFile
from django.db.models import Q
from django_pandas.io import read_frame
import logging
from delab.models import Tweet, ConversationFlow
from django_project import settings


def update_sentiment_flows():
    tweets = Tweet.objects.filter(
        (Q(sentiment="positive") | Q(sentiment="negative")) & Q(conversation_flow_id__isnull=True)).all()
    df = read_frame(tweets, fieldnames=["id",
                                        "conversation_id",
                                        "sentiment",
                                        "sentiment_value",
                                        "created_at",
                                        "tn_level",
                                        "tn_order"])
    conversation_ids = df['conversation_id'].unique()
    for conversation_id in conversation_ids:
        compute_sentiment_flow_for_conversation(conversation_id, df)


def compute_sentiment_flow_for_conversation(conversation_id, df):
    df_subset = df[df.conversation_id == conversation_id]
    df_subset = df_subset.sort_values(by=['created_at'])
    df_subset.reset_index(drop=True, inplace=True)
    rolling_column = df_subset['sentiment_value'].rolling(3).mean()
    df_subset = df_subset.assign(rolling_sentiment=rolling_column)
    plot = df_subset.plot(y=['rolling_sentiment', 'sentiment_value'], use_index=True)
    image_path = ConversationFlow.image.field.upload_to + "/" \
                    + str(conversation_id) + ".jpg"
    download_path = settings.MEDIA_ROOT + "/" \
                    + image_path
    logging.debug("saving the conversation_flow_pic to {}".format(download_path))

    plot.figure.savefig(download_path, format="jpg")
    # content_file = ImageFile(download_path)
    flow = ConversationFlow.create(image_path)
    flow.save()

    tweets = Tweet.objects.filter(conversation_id=conversation_id).all()
    tweets.update(conversation_flow=flow)
