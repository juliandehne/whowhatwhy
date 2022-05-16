from django.db.models import Count

from delab.models import TWCandidateIntolerance


def run():
    """
    candidates = TWCandidateIntolerance.objects.filter(first_bad_word__isnull=True, political_correct_word__isnull=True) \
        .annotate(Count('twintolerancerating')).exclude(twintolerancerating__count__gt=0).all()

    for candidate in candidates:
        candidate.delete()
    """