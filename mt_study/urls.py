from django.urls import path

from mt_study.views import InterventionCreateView, NoMoreDiscussionsView, intervention_proxy, classification_proxy, \
    ClassificationCreateView, NoMoreClassificationsView, intervention_sent_view_proxy, InterventionSentView, HelpView

urlpatterns = [
    # the patterns for the writing up the moderation view
    path('intervention/<int:flow_id>', InterventionCreateView.as_view(),
         name='mt_study-create-intervention'),
    path('intervention_proxy', intervention_proxy,
         name='mt_study-proxy'),
    path('intervention/nomore', NoMoreDiscussionsView.as_view(),
         name='mt_study-nomore'),

    # the patterns for the classification view
    path('classification/<int:flow_id>', ClassificationCreateView.as_view(),
         name='mt_study-create-classification'),
    path('', classification_proxy,
         name='mt_study-classification-proxy'),
    path('intervention/nomore', NoMoreClassificationsView.as_view(),
         name='mt_study-classification-nomore'),

    # the patterns for the classification view
    path('intervention_send/<int:pk>', InterventionSentView.as_view(),
         name='mt_study-send-intervention'),
    path('intervention_send_proxy', intervention_sent_view_proxy,
         name='mt_study-send-intervention-proxy'),
    path('intervention_send/nomore', NoMoreDiscussionsView.as_view(),
         name='mt_study-send-intervention-nomore'),
    path('help', HelpView.as_view(), name="mt_study-help")

]
