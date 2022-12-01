from random import choice

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import (
    CreateView,
    TemplateView,
    UpdateView
)

from delab.models import ModerationCandidate2
from delab.models import ModerationRating
from delab.views import compute_context
from django.urls import reverse

"""
This contains the views for the dictionary based moderation labeling project.
"""


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
    fields = ["u_mod_rating", "u_moderating_part"]

    def get_initial(self):
        initial = super().get_initial()
        candidate_id = self.request.resolver_match.kwargs['pk']
        candidate = ModerationCandidate2.objects.filter(id=candidate_id).get()
        # initial['u_moderating_part'] = candidate.tweet.text
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

        return compute_context(candidate, context)


class NoMoreRelabelCandidatesView(TemplateView):
    template_name = "delab/nomore_moderations_torelabel.html"


def moderation2_relabel_proxy(request):
    current_user = request.user
    user_coded_candidates = ModerationCandidate2.objects \
        .annotate(num_coders=Count('moderationrating')) \
        .exclude(num_coders__lt=2) \
        .filter(moderationrating__in=current_user.moderationrating_set.all()) \
        .prefetch_related('moderationrating_set') \
        .all()
    candidate_id_list = []
    for candidate in user_coded_candidates:
        other_rating = None
        user_rating = None
        for rating in candidate.moderationrating_set.select_related("mod_coder").all():
            if rating.mod_coder != current_user:
                other_rating = rating
            else:
                user_rating = rating
        if other_rating is not None:
            if (other_rating.u_mod_rating < 0 < user_rating.u_mod_rating) \
                    or (other_rating.u_mod_rating > 0 > user_rating.u_mod_rating):
                # candidate_id_list.append(candidate.id)
                candidate_id_list.append(user_rating.id)

    # candidates = ModerationCandidate2.objects.filter(id__in=candidate_id_list).all()
    candidates = ModerationRating.objects.filter(id__in=candidate_id_list).all()

    if len(candidates) == 0:
        # raise Http404("There seems no more data to label!")
        return redirect('delab-relabel-moderation2-nomore')
    candidate = choice(candidates)
    pk = candidate.pk
    return redirect('delab-relabel-moderation2', pk=pk)


class ModerationRelabelView(LoginRequiredMixin, UpdateView, SuccessMessageMixin):
    model = ModerationRating
    template_name = "delab/moderationrating_update_form.html"
    fields = ["u_mod_rating", "u_moderating_part"]

    def get_success_url(self):
        return reverse('delab-relabel-moderation2-proxy')

    """
    def get_initial(self):
        initial = super().get_initial()
        candidate_id = self.request.resolver_match.kwargs['pk']
        candidate = ModerationCandidate2.objects.filter(id=candidate_id).get()
        user_id = self.request.user.id
        u_moderating_part = candidate.moderationrating_set.filter(mod_coder_id=user_id).get().u_moderating_part
        initial['u_moderating_part'] = u_moderating_part
        return initial
    """

    """
    def form_valid(self, form):
        form.instance.mod_coder = self.request.user
        # form.instance.mod_candidate_id = self.request.resolver_match.kwargs['pk']
        # candidate = ModerationCandidate2.objects.filter(id=form.instance.candidate_id).get()
        return super().form_valid(form)
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ModerationRelabelView, self).get_context_data(**kwargs)

        rating_id = self.request.resolver_match.kwargs['pk']
        rating = ModerationRating.objects.filter(id=rating_id).get()
        # candidate = ModerationCandidate2.objects.filter(id=candidate_id).get()
        candidate = rating.mod_candidate

        moderation_rating_map = {-2: "strongly not moderating",
                                 -1: "not moderating",
                                 1: "moderating",
                                 2: "strongly moderating"}
        user_id = self.request.user.id
        # user_rating = candidate.moderationrating_set.filter(mod_coder_id=user_id).get().u_mod_rating
        user_rating = rating.u_mod_rating
        other_rating = candidate.moderationrating_set.exclude(mod_coder_id=user_id).first().u_mod_rating

        context["user_rating"] = moderation_rating_map[user_rating]
        context["other_rating"] = moderation_rating_map[other_rating]
        context = compute_context(candidate, context)
        return context
