from delab.analytics.flow_duos import get_flow_duos, get_flow_duo_windows
from django_project.settings import MAX_DUO_FLOWS_FOR_ANALYSIS


def run():
    # flow_duos = get_flow_duos(MAX_DUO_FLOWS_FOR_ANALYSIS)
    flow_duos = get_flow_duo_windows()
    for duo in flow_duos:
        print("duos are structured {} to {} ".format(len(duo.tweets1), len(duo.tweets2)))
        assert duo.common_tweets is not None
        pre_length = len(duo.common_tweets)
        assert duo.tweets2_post_branching is not None
        assert duo.tweets1_post_branching is not None
        post_length = min(len(duo.tweets1_post_branching), len(duo.tweets2_post_branching))
        print("pre_branching length = {} post_branching_length = {}".format(pre_length, post_length))
