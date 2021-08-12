from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django_countries.base import _

from twitter.models import SimpleRequest
import logging


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class SimpleRequestCreateView(CreateView):
    model = SimpleRequest
    fields = ['title']
    initial = {"title": "#covid #vaccination"}

    # success_message = "Institution %(title)s was created successfully"

    def form_valid(self, form):
        title = form.instance.title
        return super().form_valid(form)


# @class ConversationView(ListView)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        },
        'file_error': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'debug.log'
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'error.log'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'file_error']
        }
    }
})
