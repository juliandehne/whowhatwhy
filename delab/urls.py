from django.urls import path

from .views import (
    SimpleRequestCreateView
)
from blog.views import PostListView
from . import views

urlpatterns = [
    path('request/new', SimpleRequestCreateView.as_view(), name='delab-create-simple-request'),
]
