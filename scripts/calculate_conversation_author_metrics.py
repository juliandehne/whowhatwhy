from delab.analytics.author_centrality import author_centrality
from delab.api.api_util import get_all_conversation_ids
from delab.models.corpus_project_models import ConversationAuthorMetrics

"""
Computer Metrics about the conversation aggregated on the author level
"""


def run():
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        records = author_centrality(conversation_id)
        n_posts = 0  # todo write code that computes that
        is_root_author = False  # todo write code that computes that
        baseline_vision = None  # TODO write code that computes that
        for record in records:
            ConversationAuthorMetrics.objects.create(
                author_id=record["author"],
                conversation_id=record["conversation_id"],
                centrality=records["centrality_score"],
                n_posts=n_posts,
                is_root_author=is_root_author,
                baseline_vision=baseline_vision
            )
