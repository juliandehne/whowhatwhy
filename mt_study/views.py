from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.
from django.views.generic import CreateView

from mt_study.models import Intervention


class InterventionCreateView(SuccessMessageMixin, CreateView, LoginRequiredMixin):
    model = Intervention
    fields = ['text', 'moderation_type']
    # initial = {"title": "migration"}
    success_message = "The Moderation Suggestion has been created!"

    def form_valid(self, form):
        form.instance.coder = self.request.user
        flow_id = self.request.resolver_match.kwargs['flow_id']
        form.instance.flow = flow_id
        return super().form_valid(form)

    """
    def get_success_url(self):
        parent_id = self.request.resolver_match.kwargs['reply_to_id']
        parent_tweet = Tweet.objects.filter(twitter_id=parent_id).get()
        return reverse('delab-conversation', kwargs={'conversation_id': parent_tweet.conversation_id})
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(InterventionCreateView, self).get_context_data(**kwargs)
        flow_id = self.request.resolver_match.kwargs['flow_id']
        # TODO select tweets and add to context

        return context
