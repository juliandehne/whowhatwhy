from django.urls import path, include

from delab.api.view_sets import get_tabbed_conversation_view, \
    get_cropped_conversation_ids, \
    get_all_cropped_conversation_ids, get_zip_view, get_full_zip_view
from .api.router import get_routes
from .views import (
    SimpleRequestCreateView,
    ConversationListView, SimpleRequestListView, ConversationView, TopicCreateView, TaskStatusView, simple_request_proxy
)

urlpatterns = [
    path('request/new', SimpleRequestCreateView.as_view(), name='delab-create-simple-request'),
    path('topic/new', TopicCreateView.as_view(), name='delab-create-topic'),
    path('requests', SimpleRequestListView.as_view(), name='delab-conversations-requests'),
    path('conversations/simplerequest/proxy/<int:pk>', simple_request_proxy, name='simple-request-proxy'),
    path('conversations/simplerequest/status/<int:pk>', TaskStatusView.as_view(), name='simple-request-status'),
    path('conversations/simplerequest/results/<int:pk>', ConversationListView.as_view(),
         name='delab-conversations-for-request'),
    path('conversation/<int:conversation_id>', ConversationView.as_view(),
         name='delab-conversation'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('rest/migration/tweets_text/conversation/<int:conversation_id>/<str:full>', get_tabbed_conversation_view),
    path('rest/migration/tweets_text/conversation_ids', get_cropped_conversation_ids),
    path('rest/migration/tweets_text/all', get_all_cropped_conversation_ids),
    path('rest/migration/tweets_zip/conversation/<int:conversation_id>', get_zip_view),
    path('rest/migration/tweets_zip/all/<str:full>', get_full_zip_view),
    path('', include(get_routes().urls)),
    # path('rest/migration/tweets_excel/conversation/<int:conversation_id>/', TweetExcelSingleViewSet.as_view),
]
