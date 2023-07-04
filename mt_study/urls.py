from django.urls import path

from mt_study.views import InterventionCreateView, NoMoreDiscussionsView, intervention_proxy, classification_proxy, \
    ClassificationCreateView, NoMoreClassificationsView

urlpatterns = [
    # the patterns for the moderation-labeling approach 2
    path('intervention/<int:flow_id>', InterventionCreateView.as_view(),
         name='mt_study-create-intervention'),
    path('intervention_proxy', intervention_proxy,
         name='mt_study-proxy'),
    path('intervention/nomore', NoMoreDiscussionsView.as_view(),
         name='mt_study-nomore'),

    # the patterns for the moderation-labeling approach 2
    path('classification/<int:flow_id>', ClassificationCreateView.as_view(),
         name='mt_study-create-classification'),
    path('', classification_proxy,
         name='mt_study-classification-proxy'),
    path('intervention/nomore', NoMoreClassificationsView.as_view(),
         name='mt_study-classification-nomore'),
]
