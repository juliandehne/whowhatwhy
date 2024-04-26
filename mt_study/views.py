import time
from random import choice

from crispy_forms.helper import FormHelper
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.
from datetime import date
from django.utils import timezone
from datetime import timedelta

from django import forms
from django.db.models import Exists, OuterRef, Q
from django.forms import ModelForm, Form, IntegerField
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from delab.bot.moderation_bot import send_post
from delab.delab_enums import MODERATION_TYPE
from delab.models import ConversationFlow
from mt_study.logic.label_flows import needs_moderation
from mt_study.models import Intervention, Classification, validate_insert_position


class ClassificationForm(ModelForm):
    """
    def __init__(self, *args, **kwargs):
        super(ClassificationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
    """
    needs_moderation = forms.ChoiceField(
        choices=[(None, 'No moderation is needed')] + list(MODERATION_TYPE.choices),
        required=False,
        widget=forms.Select()
    )

    def __init__(self, *args, **kwargs):
        super(ClassificationForm, self).__init__(*args, **kwargs)

        # Loop through all fields
        for name, field in self.fields.items():
            # Check if the field is a BooleanField
            if isinstance(field, forms.BooleanField):
                # Adjust the field's choices and widget
                field.choices = [
                    (True, 'Yes'),
                    (False, 'No'),
                    (None, 'Not Sure')
                ]
                field.widget = forms.RadioSelect()
                field.required = False
                # field.label = None  # This removes the label
                field.label = field.help_text
                field.help_text = None

    class Meta:
        model = Classification
        # exclude = ('flow', 'coder', 'elaboration_support_3', 'norm_control_1')
        exclude = (
            'flow', 'coder', 'elaboration_support_3', 'norm_control_1',
            'is_conversation_0', 'is_conversation_1', 'is_conversation_2',
            'is_conversation_3', 'is_conversation_4', 'is_conversation_5',
            'agenda_control_1', 'agenda_control_2', 'agenda_control_3',
            'emotion_control_1', 'emotion_control_2', 'emotion_control_3',
            'participation_1', 'participation_2', 'participation_3',
            'consensus_seeking_1', 'consensus_seeking_2', 'consensus_seeking_3',
            'norm_control_2', 'norm_control_3',
            'elaboration_support_1', 'elaboration_support_2', 'is_valid_conversation'
        )


class ClassificationCreateView(SuccessMessageMixin, CreateView, LoginRequiredMixin):
    model = Classification
    form_class = ClassificationForm
    template_name = "mt_study/mt_study_classification.html"
    # initial = {"title": "migration"}
    success_message = "The Conversation has been classified!"

    def form_valid(self, form):
        form.instance.coder = self.request.user
        flow_id = self.request.resolver_match.kwargs['flow_id']
        form.instance.flow_id = flow_id
        return super().form_valid(form)

    def get_success_url(self):
        # return reverse('mt_study-classification-proxy')
        flow_url = reverse('mt_study-classification-proxy')
        return cache_buster(flow_url)

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
    languages = get_user_languages(request)

    last_hour, now = get_last_hour()

    today = date.today()
    candidate_flows = list(ConversationFlow.objects.annotate(
        has_classification=Exists(Classification.objects.filter(flow_id=OuterRef('pk'))))
                           .filter(sample_flow=today)
                           .filter(has_classification=False)
                           .filter(Q(mt_study_lock_time__lt=last_hour) | Q(mt_study_lock_time__isnull=True)).all())
    # hack after manually deleting tweets
    # candidate_flows = list(filter(lambda x: len(x.tweets.all()) > 4, candidate_flows))
    candidates = list(filter(lambda x: x.tweets.first().language in languages, candidate_flows))
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('mt_study-classification-nomore')
    candidate = choice(candidates)
    candidate.mt_study_lock_time = now
    candidate.save(update_fields=["mt_study_lock_time"])
    return redirect('mt_study-create-classification', flow_id=candidate.id)


def get_user_languages(request):
    current_user = request.user
    languages = [current_user.profile.primary_language, current_user.profile.secondary_language,
                 current_user.profile.tertiary_language]
    return languages


def get_last_hour():
    # Get the current time
    now = timezone.now()
    # Calculate the datetime range for the last hour
    # for debugging purposes changed to five minutes
    # last_hour = now - timedelta(hours=1)
    last_hour = now - timedelta(minutes=5)
    return last_hour, now


class NoMoreClassificationsView(TemplateView):
    template_name = "mt_study/nomore_classifications.html"


class InterventionCreateView(SuccessMessageMixin, CreateView, LoginRequiredMixin):
    model = Intervention
    fields = ['position_in_flow', 'text']
    template_name = "mt_study/mt_study_intervention.html"
    # initial = {"title": "migration"}
    success_message = "The Moderation Suggestion has been created!"

    def form_valid(self, form):
        form.instance.coder = self.request.user
        flow_id = self.request.resolver_match.kwargs['flow_id']
        form.instance.flow_id = flow_id
        validate_insert_position(form.instance.position_in_flow, form.instance)
        return super().form_valid(form)

    def get_success_url(self):
        # return reverse('mt_study-proxy')
        flow_url = reverse('mt_study-proxy')
        return cache_buster(flow_url)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(InterventionCreateView, self).get_context_data(**kwargs)
        flow_id = self.request.resolver_match.kwargs['flow_id']
        flow = ConversationFlow.objects.filter(id=flow_id).first()
        tweets = flow.tweets.all()
        tweets = list(sorted(tweets, key=lambda x: x.created_at, reverse=False))
        # tweets = tweets[-5:]
        classification = Classification.objects.filter(flow_id=flow_id).first()
        context["tweets"] = tweets
        context["classification"] = classification.needs_moderation
        return context


@login_required
def intervention_proxy(request):
    languages = get_user_languages(request)

    today = date.today()
    last_hour, now = get_last_hour()

    flows = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .annotate(has_classification=Exists(Classification.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=False) \
        .filter(has_classification=True) \
        .filter(Q(mt_study_lock_time_write__lt=last_hour) | Q(mt_study_lock_time_write__isnull=True)).all()

    flows = list(filter(needs_moderation, flows))
    flows = list(filter(lambda x: x.tweets.first().language in languages, flows))

    if len(flows) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('mt_study-nomore')
    candidate = choice(flows)
    candidate.mt_study_lock_time_write = now
    candidate.save(update_fields=["mt_study_lock_time_write"])

    return redirect('mt_study-create-intervention', flow_id=candidate.pk)
    # Construct the base URL.


class NoMoreDiscussionsView(TemplateView):
    template_name = "mt_study/nomore_interventions.html"


class InterventionSentView(SuccessMessageMixin, UpdateView, LoginRequiredMixin):
    model = Intervention
    fields = ['text', 'sendable']
    template_name = "mt_study/mt_study_send_intervention.html"
    # initial = {"title": "migration"}
    success_message = "The M" \
                      "oderation was saved and possibly posted!"

    def form_valid(self, form):
        form.instance.sendable_coder = self.request.user
        intervention_id = self.request.resolver_match.kwargs['pk']
        if form.instance.sendable:
            send_post(intervention_id)
        return super().form_valid(form)

    def get_success_url(self):
        # return reverse('mt_study-send-intervention-proxy')
        flow_url = reverse('mt_study-send-intervention-proxy')
        return cache_buster(flow_url)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(InterventionSentView, self).get_context_data(**kwargs)
        intervention_id = self.request.resolver_match.kwargs['pk']
        flow = Intervention.objects.filter(id=intervention_id).first().flow
        tweets = flow.tweets.all()
        tweets = list(sorted(tweets, key=lambda x: x.created_at, reverse=False))
        # tweets = tweets[-5:]
        context["tweets"] = tweets
        return context


@login_required
def intervention_sent_view_proxy(request):
    languages = get_user_languages(request)

    today = date.today()
    last_hour, now = get_last_hour()

    flows = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=True) \
        .filter(Q(mt_study_lock_time_send__lt=last_hour) | Q(mt_study_lock_time_send__isnull=True)).all()

    flows = list(filter(lambda x: x.tweets.first().language in languages, flows))

    interventions = list(Intervention.objects.filter(flow__in=flows) \
                         .exclude(sent=True) \
                         .exclude(sendable=True).all() \
                         .exclude(sendable=False).all())

    if len(interventions) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('mt_study-send-intervention-nomore')
    candidate = choice(interventions)
    candidate.flow.mt_study_lock_time_send = now
    candidate.flow.save(update_fields=["mt_study_lock_time_send"])
    return redirect('mt_study-send-intervention', pk=candidate.id)


class HelpView(TemplateView):
    template_name = 'mt_study/help.html'


class StatusForm(Form):
    n_classified_today = IntegerField()
    n_written_today = IntegerField()
    n_send_today = IntegerField()

    n_classified_today_by_you = IntegerField()
    n_written_today_by_you = IntegerField()
    n_send_today_by_you = IntegerField()

    n_classify_available_today = IntegerField()
    n_write_available_today = IntegerField()
    n_send_available_today = IntegerField()

    n_classify_available_today_for_you = IntegerField()
    n_write_available_today_for_you = IntegerField()
    n_sendable_available_today_for_you = IntegerField()


# views.py

def custom_query(request):
    current_user = request.user
    today = date.today()
    classification_flows_today = ConversationFlow.objects.annotate(
        has_classification=Exists(Classification.objects
                                  .filter(flow_id=OuterRef('pk')))).filter(sample_flow=today) \
        .filter(has_classification=True)

    classification_flows_today_by_you = ConversationFlow.objects.annotate(
        has_classification=Exists(Classification.objects
                                  .filter(flow_id=OuterRef('pk')).filter(coder=current_user))) \
        .filter(sample_flow=today) \
        .filter(has_classification=True)

    intervention_written_today = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .annotate(has_classification=Exists(Classification.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=True) \
        .filter(has_classification=True)

    intervention_written_today_by_you = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .annotate(has_classification=Exists(Classification.objects
                                            .filter(flow_id=OuterRef('pk'))
                                            .filter(coder=current_user))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=True) \
        .filter(has_classification=True)

    intervention_sent_today = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects
                                          .filter(flow_id=OuterRef('pk'))
                                          .filter(sendable__isnull=False))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=True)

    intervention_sent_today_by_you = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects
                                          .filter(flow_id=OuterRef('pk'))
                                          .filter(sendable__isnull=False)
                                          .filter(sendable_coder=current_user))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=True)

    n_classify_available_today = ConversationFlow.objects.annotate(
        has_classification=Exists(Classification.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_classification=False)

    languages = get_user_languages(request)
    n_classify_available_today_for_you = len(list(filter(lambda x: x.tweets.first().language in languages,
                                                         n_classify_available_today.all())))

    n_write_available_today = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .annotate(has_classification=Exists(Classification.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=False) \
        .filter(has_classification=True)

    n_write_available_today = list(filter(needs_moderation, n_write_available_today))

    n_write_available_today_for_you = len(list(filter(lambda x: x.tweets.first().language in languages,
                                                      n_write_available_today)))

    n_send_available_today = ConversationFlow.objects \
        .annotate(has_intervention=Exists(Intervention.objects.filter(flow_id=OuterRef('pk')))) \
        .filter(sample_flow=today) \
        .filter(has_intervention=True).filter(intervention__sendable__isnull=True)

    n_sendable_available_today_for_you = len(list(filter(lambda x: x.tweets.first().language in languages,
                                                         n_send_available_today.all())))

    filled_form = StatusForm(initial={
        'n_classified_today': classification_flows_today.count(),
        'n_written_today': intervention_written_today.count(),
        'n_send_today': intervention_sent_today.count(),
        'n_classified_today_by_you': classification_flows_today_by_you.count(),
        'n_written_today_by_you': intervention_written_today_by_you.count(),
        'n_send_today_by_you': intervention_sent_today_by_you.count(),
        'n_classify_available_today': n_classify_available_today.count(),
        'n_write_available_today': len(n_write_available_today),
        'n_send_available_today': n_send_available_today.count(),
        'n_classify_available_today_for_you': n_classify_available_today_for_you,
        'n_write_available_today_for_you': n_write_available_today_for_you,
        'n_sendable_available_today_for_you': n_sendable_available_today_for_you,
    })
    return [filled_form]


def status_read_view(request):
    data_objects = custom_query(request)

    return render(request, 'mt_study/status_read_template.html', {'forms_list': data_objects})


def cache_buster(url):
    # Generate a timestamp as a string, but it should be bytes when using quote_from_bytes
    cache_buster = str(int(time.time()))

    # If you were using quote or quote_from_bytes somewhere like this:
    # url_encoded_cache_buster = quote(cache_buster)  # This line could cause an error if not expected.

    # Correct usage without quote_from_bytes, as cache_buster is not bytes.
    flow_url_with_cache_buster = f"{url}?_={cache_buster}"

    return flow_url_with_cache_buster
