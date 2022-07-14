from random import choice

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import (
    UpdateView, TemplateView
)

from delab.models import Tweet, TWCandidate

"""
This contains the views for the formula based moderation labeling project. 
Have a look here: https://github.com/juliandehne/delab/wiki/moderation_mining
"""


class TWCandidateLabelView(LoginRequiredMixin, UpdateView, SuccessMessageMixin):
    model = TWCandidate
    fields = ['u_moderator_rating', 'u_author_topic_variance_rating', 'u_sentiment_rating']

    def form_valid(self, form):
        form.instance.coder = self.request.user
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TWCandidateLabelView, self).get_context_data(**kwargs)

        candidate_id = self.request.resolver_match.kwargs['pk']
        # candidate_id = self.query_pk_and_slug
        candidate = TWCandidate.objects.filter(id=candidate_id).get()
        tweet_text = candidate.tweet.text
        tweet_id = candidate.tweet.id
        # context["text"] = clean_corpus([tweet_text])[0]
        context["text"] = tweet_text
        context["tweet_id"] = tweet_id
        context_tweets = Tweet.objects.filter(conversation_id=candidate.tweet.conversation_id).order_by(
            'created_at')

        full_conversation = list(context_tweets.values_list("text", flat=True))
        index = full_conversation.index(tweet_text)

        # full_conversation = clean_corpus(full_conversation)
        context["conversation"] = full_conversation[index - 2:index + 3]
        return context


def candidate_label_proxy(request):
    candidates = TWCandidate.objects.filter(
        Q(coder__isnull=True) & ~Q(coded_by=request.user)).all()
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('delab-label-moderation-nomore')
    candidate = choice(candidates)
    pk = candidate.pk
    return redirect('delab-label', pk=pk)


class NoMoreModeratingCandidatesView(TemplateView):
    template_name = "delab/nomore_moderations_tolabel.html"