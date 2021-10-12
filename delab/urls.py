import django_filters
from django.urls import path, include

from rest_framework import serializers, viewsets, routers

from .api import TweetExcelViewSet, TweetViewSet, get_tabbed_conversation_view, get_cropped_conversation_ids, \
    get_all_tabbed_conversation_view
from .models import Tweet, SimpleRequest

from .views import (
    SimpleRequestCreateView,
    ConversationListView, SimpleRequestListView, ConversationView, TopicCreateView
)
from blog.views import PostListView
from . import views

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'rest/migration/tweets_excel', TweetExcelViewSet)
router.register(r'rest/migration/tweets_json', TweetViewSet)
# router.register(r'rest/migration/tweets_text', TweetTxtConversationViewSet)

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
    path('rest/migration/tweets_text/<int:conversation_id>/', get_tabbed_conversation_view),
    path('rest/migration/tweets_text/conversation_ids', get_cropped_conversation_ids),
    path('rest/migration/tweets_text/all', get_all_tabbed_conversation_view),
]
