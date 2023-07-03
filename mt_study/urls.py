from django.urls import path

from mt_study.views import InterventionCreateView, NoMoreDiscussionsView, intervention_proxy

urlpatterns = [
    # the patterns for the moderation-labeling approach 2
    path('intervention/<int:flow_id>', InterventionCreateView.as_view(),
         name='mt_study-create-intervention'),
    path('', intervention_proxy,
         name='mt_study-proxy'),
    path('intervention/nomore', NoMoreDiscussionsView.as_view(),
         name='mt_study-nomore'),
]
