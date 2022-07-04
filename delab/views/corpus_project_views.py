import datetime
from random import choice

from background_task.models import Task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView, TemplateView
)

from delab.delab_enums import PLATFORM
from delab.models import SimpleRequest, Tweet, TwTopic, TWCandidate, TweetAuthor, TWCandidateIntolerance, \
    TWIntoleranceRating, IntoleranceAnswer, IntoleranceAnswerValidation, ModerationCandidate2, ModerationRating
from delab.tasks import get_tasks_status

from django_project.settings import min_intolerance_answer_coders_needed, min_intolerance_coders_needed
from util.abusing_strings import convert_to_hash


# @method_decorator(csrf_exempt, name='dispatch')
class SimpleRequestListView(ListView):
    model = SimpleRequest
    template_name = 'delab/simple_request_list.html'
    context_object_name = 'requests'
    fields = ['created_at', 'title', 'language']
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


# @method_decorator(csrf_exempt, name='dispatch')
class ConversationView(ListView):
    model = Tweet
    template_name = 'delab/conversation.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'tweets'
    fields = ['created_at', 'text', 'author_id', 'sentiment', 'conversation_id', 'simple_request_id']
    paginate_by = 5

    def get_queryset(self):
        return Tweet.objects.filter(conversation_id=self.request.resolver_match.kwargs['conversation_id']) \
            .order_by("created_at")

    def get_context_data(self, **kwargs):
        context = super(ConversationView, self).get_context_data(**kwargs)
        # simple_request = get_object_or_404(SimpleRequest, id=self.request.resolver_match.kwargs['pk'])
        conversation_id = self.request.resolver_match.kwargs['conversation_id']
        topic = Tweet.objects.filter(conversation_id=conversation_id).first().topic.title
        context['topic'] = topic
        return context


# Create your views here.
##@method_decorator(csrf_exempt, name='dispatch')
class SimpleRequestCreateView(SuccessMessageMixin, CreateView):
    model = SimpleRequest
    fields = ['platform', 'version', 'topic', 'title', 'fast_mode', 'language']
    initial = {"title": "covid vaccination"}

    success_message = "Conversations with the request %(title)s are being downloaded now! \n" \
                      "You might have to refresh the page until we have build a loading screen!"


# Create your views here.
# #@method_decorator(csrf_exempt, name='dispatch')
class TopicCreateView(SuccessMessageMixin, CreateView):
    model = TwTopic
    fields = ['title']
    initial = {"title": "migration"}

    success_message = "The Topic has been created!"


class ModerationCreateView(SuccessMessageMixin, CreateView, LoginRequiredMixin):
    model = Tweet
    fields = ['text', 'd_comment', 'publish']
    # initial = {"title": "migration"}
    success_message = "The Moderation Suggestion has been created!"

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        form.instance.platform = PLATFORM.DELAB
        parent_id = self.request.resolver_match.kwargs['reply_to_id']
        form.instance.tn_parent_id = parent_id
        parent_tweet = Tweet.objects.filter(twitter_id=parent_id).get()
        form.instance.in_reply_to_user_id = parent_tweet.author_id
        form.instance.conversation_id = parent_tweet.conversation_id
        form.instance.simple_request_id = parent_tweet.simple_request_id
        form.instance.topic_id = parent_tweet.topic_id
        form.instance.created_at = parent_tweet.created_at + datetime.timedelta(milliseconds=1)
        form.instance.language = parent_tweet.language
        form.instance.twitter_id = convert_to_hash(form.instance.text + str(parent_id))
        return super().form_valid(form)

    def get_success_url(self):
        parent_id = self.request.resolver_match.kwargs['reply_to_id']
        parent_tweet = Tweet.objects.filter(twitter_id=parent_id).get()
        return reverse('delab-conversation', kwargs={'conversation_id': parent_tweet.conversation_id})

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ModerationCreateView, self).get_context_data(**kwargs)
        parent_id = self.request.resolver_match.kwargs['reply_to_id']
        parent_tweet = Tweet.objects.filter(twitter_id=parent_id).get()
        context["parent"] = parent_tweet.text

        return context


# @method_decorator(csrf_exempt, name='dispatch')
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
        # timelines_not_downloaded = Tweet.objects.filter(
        #    ~Exists(Timeline.objects.filter(author_id=OuterRef("author_id")))).filter(
        #    simple_request_id=simple_request.id).count()
        # context["timelines_downloaded"] = context['tweets_downloaded'] - timelines_not_downloaded
        sentiments_analyzed = simple_request.tweet_set.filter(sentiment_value__isnull=False).count()
        context["sentiments_analyzed"] = sentiments_analyzed
        flows_analyzed = simple_request.tweet_set.filter(conversation_flow__isnull=False).count()
        context["flows_analyzed"] = flows_analyzed

        # tweet_ids = simple_request.tweet_set.values_list("id", flat=True)
        timelines_downloaded = TweetAuthor.objects.filter(has_timeline=True).count()
        context["timelines_downloaded"] = timelines_downloaded
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



def downloads_view(request):
    return render(request, 'delab/downloads.html')
