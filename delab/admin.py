from django.contrib import admin


# Register your models here.
from .models import *

admin.site.register(SimpleRequest)
admin.site.register(TwTopic)
admin.site.register(ConversationFlow)
admin.site.register(TweetAuthor)
admin.site.register(Tweet)
admin.site.register(Timeline)

admin.site.register(TWCandidateIntolerance)
admin.site.register(TWIntoleranceRating)
admin.site.register(IntoleranceAnswer)
admin.site.register(IntoleranceAnswerValidation)
admin.site.register(ModerationCandidate2)
admin.site.register(ModerationRating)



# admin.site.register(Tweet, TweetAdmin)
