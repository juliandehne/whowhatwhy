from logging.handlers import RotatingFileHandler
from random import choice

from background_task.models import Task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q, Exists, OuterRef
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django_countries.base import _
from django.shortcuts import render, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from delab.models import SimpleRequest, Tweet, TwTopic, Timeline, TWCandidate
import logging
from .tasks import get_tasks_status


@method_decorator(csrf_exempt, name='dispatch')
class SimpleRequestListView(ListView):
    model = SimpleRequest
    template_name = 'delab/simple_request_list.html'
    context_object_name = 'requests'
    fields = ['created_at', 'title']
    paginate_by = 5


def simple_request_proxy(request, pk):
    """
    The idea is that if the download_process is still running in the background, the Task_Status_view shoudl be displayed.
    Otherwise, the downloaded conversations should be displayed!
    :param request:
    :param simple_request_id:
    :return:
    """
    running_tasks = get_tasks_status(pk)
    if len(running_tasks) > 0:
        return redirect('simple-request-status', pk=pk)
    else:
        return redirect('delab-conversations-for-request', pk=pk)


class ConversationListView(ListView):
    model = Tweet
    template_name = 'delab/tweet_list.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'tweets'
    fields = ['created_at', 'text', 'author_id', 'conversation_id']
    paginate_by = 5

    def get_queryset(self):
        simple_request = get_object_or_404(SimpleRequest, id=self.request.resolver_match.kwargs['pk'])
        return Tweet.objects.filter(Q(simple_request=simple_request) & Q(tn_parent__isnull=True)) \
            .order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(ConversationListView, self).get_context_data(**kwargs)
        simple_request = get_object_or_404(SimpleRequest, id=self.request.resolver_match.kwargs['pk'])
        context['simple_request'] = simple_request
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ConversationView(ListView):
    model = Tweet
    template_name = 'delab/conversation.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'tweets'
    fields = ['created_at', 'text', 'author_id', 'sentiment', 'conversation_id', 'simple_request_id']
    paginate_by = 5

    def get_queryset(self):
        return Tweet.objects.filter(conversation_id=self.request.resolver_match.kwargs['conversation_id']) \
            .order_by("-created_at")

    """
    def get_context_data(self, **kwargs):
        context = super(ConversationListView, self).get_context_data(**kwargs)
        simple_request = get_object_or_404(SimpleRequest, id=self.request.resolver_match.kwargs['pk'])
        context['simple_request'] = simple_request
        return context
    """


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class SimpleRequestCreateView(SuccessMessageMixin, CreateView):
    model = SimpleRequest
    fields = ['title', 'max_data', 'fast_mode', 'topic']
    initial = {"title": "#covid #vaccination"}

    success_message = "Conversations with the request %(title)s are being downloaded now! \n" \
                      "You might have to refresh the page until we have build a loading screen!"


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class TopicCreateView(SuccessMessageMixin, CreateView):
    model = TwTopic
    fields = ['title']
    initial = {"title": "migration"}

    success_message = "The Topic has been created!"


@method_decorator(csrf_exempt, name='dispatch')
class TaskStatusView(ListView):
    model = Task
    template_name = 'delab/task_status.html'
    context_object_name = 'tasks'
    fields = ['task_name', "task_params", "verbose_name", "last_error", "run_at"]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskStatusView, self).get_context_data(**kwargs)
        simple_request = get_object_or_404(SimpleRequest, id=self.request.resolver_match.kwargs['pk'])
        context['simple_request'] = simple_request
        context['tweets_downloaded'] = simple_request.tweet_set.count()
        authors_downloaded = simple_request.tweet_set.filter(tw_author__isnull=False).count()
        context["authors_downloaded"] = authors_downloaded
        timelines_not_downloaded = Tweet.objects.filter(
            ~Exists(Timeline.objects.filter(author_id=OuterRef("author_id")))).filter(
            simple_request_id=simple_request.id).count()
        context["timelines_downloaded"] = context['tweets_downloaded'] - timelines_not_downloaded
        sentiments_analyzed = simple_request.tweet_set.filter(sentiment_value__isnull=False).count()
        context["sentiments_analyzed"] = sentiments_analyzed
        flows_analyzed = simple_request.tweet_set.filter(conversation_flow__isnull=False).count()
        context["flows_analyzed"] = flows_analyzed
        return context

    def get_queryset(self):
        pk = self.request.resolver_match.kwargs['pk']
        tasks = Task.objects.filter(verbose_name__contains=pk)
        return tasks

    def dispatch(self, request, *args, **kwargs):
        # check if there is some video onsite
        pk = self.request.resolver_match.kwargs['pk']
        tasks = Task.objects.filter(verbose_name__contains=pk)
        if tasks.count() == 0:
            return redirect("delab-conversations-for-request", pk=pk)
        else:
            return super(TaskStatusView, self).dispatch(request, *args, **kwargs)


# TODO finish implementing
class TWCandidateLabelView(LoginRequiredMixin, UpdateView, SuccessMessageMixin):
    model = TWCandidate
    fields = ['u_moderator_rating', 'u_author_topic_variance_rating', 'u_sentiment_rating']

    def form_valid(self, form):
        form.instance.coder = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        candidates = TWCandidate.objects.filter(coder__isnull=True).select_related().all()
        candidate = choice(candidates)
        self.query_pk_and_slug = candidate.pk
        return candidate

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TWCandidateLabelView, self).get_context_data(**kwargs)

        from delab.topic.train_topic_model import clean_corpus
        candidate_id = self.query_pk_and_slug
        candidate = TWCandidate.objects.filter(id=candidate_id).get()
        tweet_text = candidate.tweet.text
        context["text"] = clean_corpus([tweet_text])[0]
        context_tweets = Tweet.objects.filter(conversation_id=candidate.tweet.conversation_id).order_by(
            '-created_at')

        full_conversation = list(context_tweets.values_list("text", flat=True))
        index = full_conversation.index(tweet_text)

        full_conversation = clean_corpus(full_conversation)
        context["conversation"] = full_conversation[index - 2:index + 3]
        return context
