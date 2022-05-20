from django.contrib import admin
from treenode.admin import TreeNodeModelAdmin
from treenode.forms import TreeNodeForm

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
admin.site.register(TWCandidate)


class TweetAdmin(TreeNodeModelAdmin):
    # set the changelist display mode: 'accordion', 'breadcrumbs' or 'indentation' (default)
    # when changelist results are filtered by a querystring,delab_intoleranceanswer
    # 'breadcrumbs' mode will be used (to preserve corpus display integrity)
    treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_ACCORDION
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_BREADCRUMBS
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_INDENTATION

    # use TreeNodeForm to automatically exclude invalid parent choices
    form = TreeNodeForm

# admin.site.register(Tweet, TweetAdmin)
