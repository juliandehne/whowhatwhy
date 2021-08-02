from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.generic import CreateView
from django_countries.base import _

from twitter.models import SimpleRequest


# Create your views here.
class SimpleRequestCreateView(CreateView):
    model = SimpleRequest
    fields = ['title']
    initial = {"title": "#covid #vaccination"}

    # success_message = "Institution %(title)s was created successfully"

    def form_valid(self, form):
        title = form.instance.title
        return super().form_valid(form)
