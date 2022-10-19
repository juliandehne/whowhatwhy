import pandas as pd

from delab.analytics.cccp_analytics import prepare_metric_records, compute_cccp_candidate_authors, \
    compute_all_cccp_authors
from delab.models import Tweet

from django.db import connection


def run():
    compute_all_cccp_authors()

