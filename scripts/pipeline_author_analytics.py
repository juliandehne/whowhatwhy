from delab.analytics.cccp_analytics import calculate_conversation_author_metrics, compute_all_cccp_authors


def run():
    print("STEP 1: calculate conversation author metrics")
    calculate_conversation_author_metrics()

    print("STEP 2: calculate cccp examples")
    compute_all_cccp_authors()