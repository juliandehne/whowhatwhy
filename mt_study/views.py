from random import choice

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.
from datetime import date

from django.db.models import Exists, OuterRef
from django.forms import ModelForm
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from delab.bot.moderation_bot import send_post
from delab.models import ConversationFlow
from mt_study.logic.label_flows import needs_moderation
from mt_study.models import Intervention, Classification, validate_insert_position


class InterventionCreateView(SuccessMessageMixin, CreateView, LoginRequiredMixin):
    model = Intervention
    fields = ['moderation_type', 'position_in_flow', 'text']
    template_name = "mt_study/mt_study.html"
    # initial = {"title": "migration"}
    success_message = "The Moderation Suggestion has been created!"

    def form_valid(self, form):
        form.instance.coder = self.request.user
        flow_id = self.request.resolver_match.kwargs['flow_id']
        form.instance.flow_id = flow_id
        validate_insert_position(form.instance.position_in_flow, form.instance)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mt_study-proxy')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(InterventionCreateView, self).get_context_data(**kwargs)
        flow_id = self.request.resolver_match.kwargs['flow_id']
        flow = ConversationFlow.objects.filter(id=flow_id).first()
        tweets = flow.tweets.all()
        tweets = list(sorted(tweets, key=lambda x: x.created_at, reverse=False))
        # tweets = tweets[-5:]
        context["tweets"] = tweets
        # TODO select tweets and add to context

        return context


@login_required
def intervention_proxy(request):
    # current_user = request.user
    today = date.today()

    flows = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .annotate(has_classification=Exists(Classification.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=False) \
        .filter(has_classification=True)

    flows = list(filter(needs_moderation, flows))

    candidates = list(map(lambda x: x.id, flows))
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('mt_study-nomore')
    candidate = choice(candidates)
    return redirect('mt_study-create-intervention', flow_id=candidate)


class NoMoreDiscussionsView(TemplateView):
    template_name = "mt_study/nomore_interventions.html"


class InterventionSentView(SuccessMessageMixin, UpdateView, LoginRequiredMixin):
    model = Intervention
    fields = ['moderation_type', 'text', 'sendable']
    template_name = "mt_study/mt_study.html"
    # initial = {"title": "migration"}
    success_message = "The Moderation was posted!"

    def form_valid(self, form):
        form.instance.sendable_coder = self.request.user
        intervention_id = self.request.resolver_match.kwargs['pk']
        if form.instance.sendable:
            send_post(intervention_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mt_study-proxy')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(InterventionSentView, self).get_context_data(**kwargs)
        intervention_id = self.request.resolver_match.kwargs['pk']
        flow = Intervention.objects.filter(id=intervention_id).first().flow
        tweets = flow.tweets.all()
        tweets = list(sorted(tweets, key=lambda x: x.created_at, reverse=False))
        # tweets = tweets[-5:]
        context["tweets"] = tweets
        # TODO select tweets and add to context

        return context

    """
    def send_out_moderating_post(self, intervention_id):
        send_post(intervention_id)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        intervention_id = self.request.resolver_match.kwargs['pk']
        if self.object.sendable:
            self.send_out_moderating_post(intervention_id)
        return super().post(request, *args, **kwargs)
    """


@login_required
def intervention_sent_view_proxy(request):
    # current_user = request.user
    today = date.today()

    flows = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=True)

    interventions = Intervention.objects.filter(flow__in=flows) \
        .exclude(sent=True) \
        .exclude(sendable=False)

    candidates = list(map(lambda x: x.id, interventions))
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('mt_study-send-intervention-nomore')
    candidate = choice(candidates)
    return redirect('mt_study-send-intervention', pk=candidate)


class ClassificationForm(ModelForm):
    class Meta:
        model = Classification
        exclude = ('flow',)


class ClassificationCreateView(SuccessMessageMixin, CreateView, LoginRequiredMixin):
    model = Classification
    form_class = ClassificationForm
    template_name = "mt_study/mt_study.html"
    # initial = {"title": "migration"}
    success_message = "The Conversation has been classified!"

    def form_valid(self, form):
        form.instance.coder = self.request.user
        flow_id = self.request.resolver_match.kwargs['flow_id']
        form.instance.flow_id = flow_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mt_study-classification-proxy')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ClassificationCreateView, self).get_context_data(**kwargs)
        flow_id = self.request.resolver_match.kwargs['flow_id']
        flow = ConversationFlow.objects.filter(id=flow_id).first()
        tweets = flow.tweets.all()
        tweets = list(sorted(tweets, key=lambda x: x.created_at, reverse=False))
        # tweets = tweets[-5:]
        context["tweets"] = tweets
        # TODO select tweets and add to context

        return context


@login_required
def classification_proxy(request):
    # current_user = request.user
    today = date.today()
    candidates = list(ConversationFlow.objects.annotate(
        has_classification=Exists(Classification.objects.filter(flow_id=OuterRef('pk'))))
                      .filter(sample_flow=today)
                      .filter(has_classification=False).values_list("id", flat=True))
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('mt_study-classification-nomore')
    candidate = choice(candidates)
    return redirect('mt_study-create-classification', flow_id=candidate)


class NoMoreClassificationsView(TemplateView):
    template_name = "mt_study/nomore_classifications.html"
