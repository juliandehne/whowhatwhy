from rest_framework import routers

from delab.api.view_sets import TweetExcelViewSet, TweetViewSet, TweetExcelSingleViewSet, TweetSingleViewSet, \
    ModerationRatingTweetSet, TweetSequenceStatViewSet, ConversationFlowViewSet, FlowDuoTweetSet, FlowDuoWindowTweetSet


def get_routes():
    # Routers provide a way of automatically determining the URL conf.
    router = routers.DefaultRouter()
    router.register(r'rest/conversation/(?P<conversation_id>\d+)/flows', ConversationFlowViewSet,
                    basename="conversation_flows")
    router.register(r'rest/(?P<topic>\D+)/sequence_stats', TweetSequenceStatViewSet)
    router.register(r'rest/(?P<topic>\D+)/tweets_excel', TweetExcelViewSet)
    router.register(r'rest/(?P<topic>\D+)/tweets_json', TweetViewSet)
    router.register(r'rest/moderation_ratings', ModerationRatingTweetSet)
    router.register(r'rest/(?P<topic>\D+)/tweets_excel/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)',
                    TweetExcelSingleViewSet)
    router.register(r'rest/(?P<topic>\D+)/tweets_json/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)',
                    TweetSingleViewSet),
    router.register(r'rest/duoflows', FlowDuoTweetSet, basename="duoflows")
    router.register(r'rest/duoflowwindows', FlowDuoWindowTweetSet, basename="duoflowwindows")
    return router
