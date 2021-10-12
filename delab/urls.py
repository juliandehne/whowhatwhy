import django_filters
from django.urls import path, include

from rest_framework import serializers, viewsets, routers

from .api import TweetExcelViewSet, TweetViewSet
from .models import Tweet, SimpleRequest

from .views import (
    SimpleRequestCreateView,
    ConversationListView, SimpleRequestListView, ConversationView, TopicCreateView
)
from blog.views import PostListView
from . import views

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
