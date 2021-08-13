from django.urls import path

from .views import (
    SimpleRequestCreateView,
    ConversationListView
)
from blog.views import PostListView
from . import views

urlpatterns = [
    path('request/new', SimpleRequestCreateView.as_view(), name='delab-create-simple-request'),
    path('conversations/simplerequest/<int:pk>', ConversationListView.as_view(), name='delab-conversations-for-request'),
]
