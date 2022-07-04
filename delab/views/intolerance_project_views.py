from random import choice

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import (
    CreateView,
    TemplateView
)

from delab.models import Tweet, TWCandidateIntolerance, \
    TWIntoleranceRating, IntoleranceAnswer, IntoleranceAnswerValidation, ModerationCandidate2
from django_project.settings import min_intolerance_answer_coders_needed, min_intolerance_coders_needed


class TWCandidateIntoleranceLabelView(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    """
    This is a classical create view. It allows for a user rating whether a tweet is intolerant
    to be registered.
    """
    model = TWIntoleranceRating
    fields = ['u_person_hate', 'u_clearness_rating', 'user_category', 'u_intolerance_rating', 'u_sentiment_rating',
              'u_political_correct_word']

    def get_initial(self):
        initial = super().get_initial()
        candidate_id = self.request.resolver_match.kwargs['pk']
        candidate = TWCandidateIntolerance.objects.filter(id=candidate_id).get()
        initial['u_political_correct_word'] = candidate.political_correct_word
        return initial

    def form_valid(self, form):
        form.instance.coder = self.request.user
        form.instance.candidate_id = self.request.resolver_match.kwargs['pk']
        candidate_political_correct_word = form.cleaned_data.get("u_political_correct_word", "")
        candidate = TWCandidateIntolerance.objects.filter(id=form.instance.candidate_id).get()
        candidate.political_correct_word = candidate_political_correct_word
        candidate.save(update_fields=["political_correct_word"])
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TWCandidateIntoleranceLabelView, self).get_context_data(**kwargs)

        candidate_id = self.request.resolver_match.kwargs['pk']

        candidate = TWCandidateIntolerance.objects.filter(id=candidate_id).get()

        tweet_text = candidate.tweet.text
        tweet_id = candidate.tweet.id
        # context["text"] = clean_corpus([tweet_text])[0]
        context["text"] = tweet_text
        context["tweet_id"] = tweet_id
        context_tweets = Tweet.objects.filter(conversation_id=candidate.tweet.conversation_id) \
            .order_by('-created_at')

        full_conversation = list(context_tweets.values_list("text", flat=True))
        index = full_conversation.index(tweet_text)

        # full_conversation = clean_corpus(full_conversation)
        context["conversation"] = full_conversation[index - 2:index + 3]
        return context


def intolerance_candidate_label_proxy(request):
    """
    This randomly selects candidates to be labeled from the candidatestable that were preselected based on a dictionary approach
    It then redirects to the create-view where the labeling of the candidate takes place.
    :param request:
    :return:
    """
    current_user = request.user
    candidates = TWCandidateIntolerance.objects \
        .annotate(num_coders=Count('twintolerancerating')) \
        .filter(num_coders__lt=min_intolerance_coders_needed) \
        .exclude(twintolerancerating__in=current_user.twintolerancerating_set.all()) \
        .all()
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('delab-label-intolerance-nomore')
    candidate = choice(candidates)
    pk = candidate.pk
    return redirect('delab-label-intolerance', pk=pk)


def intolerance_answer_validation_proxy(request):
    current_user = request.user
    candidates = IntoleranceAnswer.objects \
        .filter(twitter_id__isnull=True) \
        .annotate(num_coders=Count('intoleranceanswervalidation')) \
        .filter(num_coders__lt=min_intolerance_answer_coders_needed) \
        .exclude(intoleranceanswervalidation__in=current_user.intoleranceanswervalidation_set.all()) \
        .all()
    if len(candidates) == 0:
        # raise Http404("There seems no more answers to validate!")
        return redirect('delab-intolerance-answer-validation-nomore')
    candidate = choice(candidates)
    pk = candidate.pk
    return redirect('delab-intolerance-answer-validation', pk=pk)





class IntoleranceAnswerValidationView(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = IntoleranceAnswerValidation
    fields = ["valid", "comment"]

    def form_valid(self, form):
        form.instance.coder = self.request.user
        form.instance.answer_id = self.request.resolver_match.kwargs['pk']
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IntoleranceAnswerValidationView, self).get_context_data(**kwargs)

        answer_id = self.request.resolver_match.kwargs['pk']

        answer = IntoleranceAnswer.objects.filter(id=answer_id).get()

        tweet_text = answer.candidate.tweet.text
        tweet_id = answer.candidate.tweet.id

        context["text"] = tweet_text
        context["tweet_id"] = tweet_id

        # NOT SURE, whether the whole context should be displayed again (may not fit)
        # context_tweets = Tweet.objects.filter(conversation_id=answer.candidate.tweet.conversation_id).order_by(
        #    '-created_at')

        # full_conversation = list(context_tweets.values_list("text", flat=True))
        # index = full_conversation.index(tweet_text)

        # full_conversation = clean_corpus(full_conversation)
        # context["conversation"] = full_conversation[index - 2:index + 3]
        context["answer1"] = answer.answer1
        context["answer2"] = answer.answer2
        context["answer3"] = answer.answer3

        return context


class NoMoreIntolerantCandidatesView(TemplateView):
    template_name = "delab/nomore_intolerant_tweets_tolabel.html"


class NoMoreAnswersToValidateView(TemplateView):
    template_name = "delab/nomore_answers_tovalidate.html"
