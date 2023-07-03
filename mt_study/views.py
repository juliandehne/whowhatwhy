from random import choice

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.
from datetime import date

from django.db.models import Exists, OuterRef
from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView

from delab.models import ConversationFlow
from mt_study.models import Intervention


class InterventionCreateView(SuccessMessageMixin, CreateView, LoginRequiredMixin):
    model = Intervention
    fields = ['text', 'moderation_type']
    template_name = "mt_study/mt_study.html"
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
        flow = ConversationFlow.objects.filter(id=flow_id).first()
        context["tweets"] = flow.tweets.all()
        # TODO select tweets and add to context

        return context


def intervention_proxy(request):
    # current_user = request.user
    today = date.today()
    candidates = list(ConversationFlow.objects.annotate(
        has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk'))))
                      .filter(sample_flow=today)
                      .filter(has_intervention=False).values_list("id", flat=True))
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('mt_study-nomore')
    candidate = choice(candidates)
    return redirect('mt_study-create-intervention', flow_id=candidate)


class NoMoreDiscussionsView(TemplateView):
    template_name = "mt_study/nomore_interventions.html"
