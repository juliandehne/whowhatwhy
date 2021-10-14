from django.urls import path, include

from rest_framework import routers

from delab.api.view_sets import TweetExcelViewSet, TweetViewSet, get_tabbed_conversation_view, \
    get_cropped_conversation_ids, \
    get_all_cropped_conversation_ids, TweetExcelSingleViewSet, TweetSingleViewSet, get_zip_view, get_full_zip_view

from .views import (
    SimpleRequestCreateView,
    ConversationListView, SimpleRequestListView, ConversationView, TopicCreateView
)

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'rest/migration/tweets_excel', TweetExcelViewSet)
router.register(r'rest/migration/tweets_json', TweetViewSet)
# router.register(r'rest/migration/tweets_text', TweetTxtConversationViewSet)
router.register(r'rest/migration/tweets_excel/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)',
                TweetExcelSingleViewSet)
router.register(r'rest/migration/tweets_json/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)',
                TweetSingleViewSet)
# router.register(r'rest/migration/tweets_zip/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)', ZipViewSet)

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
    path('rest/migration/tweets_text/conversation/<int:conversation_id>/<str:full>', get_tabbed_conversation_view),
    path('rest/migration/tweets_text/conversation_ids', get_cropped_conversation_ids),
    path('rest/migration/tweets_text/all', get_all_cropped_conversation_ids),
    path('rest/migration/tweets_zip/conversation/<int:conversation_id>', get_zip_view),
    path('rest/migration/tweets_zip/all/<str:full>', get_full_zip_view)
    # path('rest/migration/tweets_excel/conversation/<int:conversation_id>/', TweetExcelSingleViewSet.as_view),
]
