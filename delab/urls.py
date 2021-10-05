import django_filters
from django.urls import path, include
from django_filters.rest_framework import DjangoFilterBackend
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from rest_framework import serializers, viewsets, routers
from .models import Tweet, SimpleRequest

from .views import (
    SimpleRequestCreateView,
    ConversationListView, SimpleRequestListView, ConversationView, TopicCreateView
)
from blog.views import PostListView
from . import views


# Serializers define the API representation.
class TweetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tweet
        fields = ['id', 'twitter_id', 'text', 'conversation_id', 'author_id', 'created_at', 'in_reply_to_user_id',
                  'tn_children_pks',
                  'tn_order',
                  'sentiment_value', 'language']


def get_migration_query_set():
    queryset = Tweet.objects.filter(simple_request__topic__title="migration", language="en").all()
    return queryset


# ViewSets define the view behavior.
class TweetViewSet(viewsets.ModelViewSet):
    queryset = get_migration_query_set()
    serializer_class = TweetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation_id', 'tn_order', 'author_id']
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


# ViewSets define the view behavior.
class TweetExcelViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    queryset = get_migration_query_set()
    serializer_class = TweetSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'twitter_migration_export.xlsx'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation_id', 'tn_order', 'author_id']


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'migration/tweets/excel', TweetExcelViewSet)
router.register(r'migration/tweets', TweetViewSet)

urlpatterns = [
    path('request/new', SimpleRequestCreateView.as_view(), name='delab-create-simple-request'),
    path('topic/new', TopicCreateView.as_view(), name='delab-create-topic'),
    path('requests', SimpleRequestListView.as_view(), name='delab-conversations-requests'),
    path('conversations/simplerequest/<int:pk>', ConversationListView.as_view(),
         name='delab-conversations-for-request'),
    path('conversation/<int:conversation_id>', ConversationView.as_view(),
         name='delab-conversation'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
