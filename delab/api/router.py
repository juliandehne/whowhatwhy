from rest_framework import routers

from delab.api.view_sets import TweetExcelViewSet, TweetViewSet, TweetExcelSingleViewSet, TweetSingleViewSet, \
    CandidateExcelViewSet


def get_routes():
    # Routers provide a way of automatically determining the URL conf.
    router = routers.DefaultRouter()
    router.register(r'rest/(?P<topic>\D+)/tweets_excel', TweetExcelViewSet)
    router.register(r'rest/(?P<topic>\D+)/tweets_json', TweetViewSet)
    # router.register(r'rest/migration/tweets_text', TweetTxtConversationViewSet)
    router.register(r'rest/(?P<topic>\D+)/tweets_excel/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)',
                    TweetExcelSingleViewSet)
    router.register(r'rest/(?P<topic>\D+)/tweets_json/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)',
                    TweetSingleViewSet),
    router.register(r'rest/candidates_excel', CandidateExcelViewSet)
    # router.register(r'rest/migration/tweets_zip/conversation/(?P<conversation_id>\d+)/(?P<full>\D+)', ZipViewSet)
    return router
