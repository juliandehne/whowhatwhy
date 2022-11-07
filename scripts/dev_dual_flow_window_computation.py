from delab.analytics.flow_duos import get_flow_duos
from django_project.settings import MAX_DUO_FLOWS_FOR_ANALYSIS


def run():
    flow_duos = get_flow_duos(MAX_DUO_FLOWS_FOR_ANALYSIS)
    for duo in flow_duos:
        print("duos are structured {} to {} ".format(len(duo.tweets1), len(duo.tweets2)))
