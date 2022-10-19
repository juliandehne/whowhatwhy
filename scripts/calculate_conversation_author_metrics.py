import django.db.utils

from delab.analytics.author_centrality import author_centrality
from delab.analytics.cccp_analytics import calculate_author_baseline_visions, calculate_n_posts, is_root_author
from delab.api.api_util import get_all_conversation_ids
from delab.models.corpus_project_models import ConversationAuthorMetrics, TweetAuthor

"""
Computer Metrics about the conversation aggregated on the author level
"""


def run():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        try:
            author2Centrality = {}
            records = author_centrality(conversation_id)
        except AssertionError as ae:
            print("dysfunctional conversation tree found")
            continue
        baseline_visions = calculate_author_baseline_visions(conversation_id)
        for record in records:
            author = record["author"]
            conversation_id = record["conversation_id"]
            centrality_score = record["centrality_score"]
            if author in author2Centrality:
                author2Centrality[author] = author2Centrality[author] + centrality_score
            else:
                author2Centrality[author] = centrality_score

        for author in author2Centrality.keys():
            n_posts = calculate_n_posts(author,
                                        conversation_id)
            centrality_score = author2Centrality[author] / n_posts
            is_root_author_v = is_root_author(author,
                                              conversation_id)
            baseline_vision = baseline_visions[author]

            try:
                tw_author = TweetAuthor.objects.filter(twitter_id=author).get()
                ConversationAuthorMetrics.objects.create(
                    author=tw_author,
                    conversation_id=conversation_id,
                    centrality=centrality_score,
                    n_posts=n_posts,
                    is_root_author=is_root_author_v,
                    baseline_vision=baseline_vision
                )
            except django.db.utils.IntegrityError as saving_metric_exception:
                # print(saving_metric_exception)
                pass
            except django.db.utils.DataError as date_error:
                print(date_error)

