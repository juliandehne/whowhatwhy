from django_filters.rest_framework import DjangoFilterBackend
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
from rest_framework import serializers, viewsets, routers



# Serializers define the API representation.
from delab.models import Tweet

tweet_fields_used = ['id', 'twitter_id', 'text', 'conversation_id', 'author_id', 'created_at', 'in_reply_to_user_id',
                     'tn_children_pks',
                     'tn_order',
                     'sentiment_value', 'language']


class TweetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tweet
        fields = tweet_fields_used


def get_migration_query_set():
    queryset = Tweet.objects.filter(simple_request__topic__title="migration").all()
    df = queryset.to_dataframe(tweet_fields_used, index_col='id')
    # crop_trees(df) TODO
    return queryset


# ViewSets define the view behavior.
class TweetViewSet(viewsets.ModelViewSet):
    queryset = get_migration_query_set()
    serializer_class = TweetSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['conversation_id', 'tn_order', 'author_id', 'language']
    filterset_fields = tweet_fields_used
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


# ViewSets define the view behavior.
class TweetExcelViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    queryset = get_migration_query_set()
    serializer_class = TweetSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'twitter_migration_export.xlsx'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = tweet_fields_used
    # filterset_fields = ['conversation_id', 'tn_order', 'author_id', 'language']
