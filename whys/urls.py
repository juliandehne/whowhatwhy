from django.contrib import admin
from django.urls import path
from whys import views

urlpatterns = [
    path('', views.home, name="'whys-home"),
    path('about/', views.about, name="'blog-about"),
]
