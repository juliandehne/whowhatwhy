from random import choice

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import (
    CreateView,
    TemplateView
)

from delab.models import ModerationCandidate2
from delab.models import Tweet, ModerationRating


class NoMoreModeratingCandidatesView2(TemplateView):
    template_name = "delab/nomore_moderations_tolabel2.html"


def moderation2_label_proxy(request):
    current_user = request.user
    candidates = ModerationCandidate2.objects \
        .annotate(num_coders=Count('moderationrating')) \
        .filter(num_coders__lt=2) \
        .exclude(moderationrating__in=current_user.moderationrating_set.all()) \
        .all()
    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('delab-label-moderation2-nomore')
    candidate = choice(candidates)
    pk = candidate.pk
    return redirect('delab-label-moderation2', pk=pk)


class ModerationLabelView2(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = ModerationRating
    fields = ["u_mod_rating", "u_sis_issues", "u_sit_consensus", "u_mod_issues", "u_mod_consensus",
              "u_clearness_rating", "u_moderating_part"]

    def get_initial(self):
        initial = super().get_initial()
        candidate_id = self.request.resolver_match.kwargs['pk']
        candidate = ModerationCandidate2.objects.filter(id=candidate_id).get()
        initial['u_moderating_part'] = candidate.tweet.text
        return initial

    def form_valid(self, form):
        form.instance.mod_coder = self.request.user
        form.instance.mod_candidate_id = self.request.resolver_match.kwargs['pk']
        # candidate = ModerationCandidate2.objects.filter(id=form.instance.candidate_id).get()
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ModerationLabelView2, self).get_context_data(**kwargs)

        candidate_id = self.request.resolver_match.kwargs['pk']
        candidate = ModerationCandidate2.objects.filter(id=candidate_id).get()

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
