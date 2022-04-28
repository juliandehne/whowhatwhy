from django.urls import path, include

from delab.api.view_sets import get_tabbed_conversation_view, \
    get_cropped_conversation_ids, \
    get_all_conversations_tabbed, get_zip_view, get_full_zip_view, get_xml_conversation_view
from .api.router import get_routes
from .views import (
    SimpleRequestCreateView,
    ConversationListView, SimpleRequestListView, ConversationView, TopicCreateView, TaskStatusView,
    simple_request_proxy, TWCandidateLabelView, ModerationCreateView, candidate_label_proxy, downloads_view,
    TWCandidateIntoleranceLabelView, intolerance_candidate_label_proxy, intolerance_answer_validation_proxy,
    IntoleranceAnswerView
)

urlpatterns = [
    path('answer/validation/<int:pk>', IntoleranceAnswerView.as_view(), name='delab-intolerance-answer-validation'),
    path('proxy/answer/validation', intolerance_answer_validation_proxy, name='delab-intolerance-answer-validation-proxy'),


    path('label/intolerance/<int:pk>', TWCandidateIntoleranceLabelView.as_view(), name='delab-label-intolerance'),
    path('labelproxy/intolerance', intolerance_candidate_label_proxy, name='delab-label-intolerance-proxy'),
    path('label/<int:pk>', TWCandidateLabelView.as_view(), name='delab-label'),
    path('labelproxy', candidate_label_proxy, name='delab-label-proxy'),
    path('request/new', SimpleRequestCreateView.as_view(), name='delab-create-simple-request'),
    path('moderation/new/<int:reply_to_id>', ModerationCreateView.as_view(), name='delab-moderation-create'),
    path('topic/new', TopicCreateView.as_view(), name='delab-create-topic'),
    path('requests', SimpleRequestListView.as_view(), name='delab-conversations-requests'),
    path('conversations/simplerequest/proxy/<int:pk>', simple_request_proxy, name='simple-request-proxy'),
    path('conversations/simplerequest/status/<int:pk>', TaskStatusView.as_view(), name='simple-request-status'),
    path('conversations/simplerequest/results/<int:pk>', ConversationListView.as_view(),
         name='delab-conversations-for-request'),
    path('conversation/<int:conversation_id>', ConversationView.as_view(),
         name='delab-conversation'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('rest/<str:topic>/tweets_text/conversation/<int:conversation_id>/<str:full>', get_tabbed_conversation_view),
    path('rest/<str:topic>/tweets_xml/conversation/<int:conversation_id>/<str:full>', get_xml_conversation_view,
         name="delab-conversation-xml"),
    path('rest/<str:topic>/tweets_text/conversation_ids', get_cropped_conversation_ids),
    path('rest/<str:topic>/tweets_text/all', get_all_conversations_tabbed),
    path('rest/<str:topic>/tweets_zip/conversation/<int:conversation_id>', get_zip_view),
    path('rest/<str:topic>/tweets_zip/all/<str:full>', get_full_zip_view),
    path('downloads', downloads_view, name='delab-downloads'),
    path('', include(get_routes().urls)),
    # path('rest/migration/tweets_excel/conversation/<int:conversation_id>/', TweetExcelSingleViewSet.as_view),
]
