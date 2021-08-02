from django.contrib import admin

# Register your models here.
from .models import Conversation
from .models import SimpleRequest
from .models import Tweet
from .models import TwTopic

admin.site.register(Conversation)
admin.site.register(SimpleRequest)
admin.site.register(Tweet)
admin.site.register(TwTopic)
