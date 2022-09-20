from delab.api.view_sets import get_tweet_sequence_stats


def run():
    query_set = get_tweet_sequence_stats("culturalscripts")
    if query_set is not None:
        for stats in query_set[:5]:
            print(stats.conversation_id)
            print(stats.found_tweets)
            print(stats.not_found_tweets)
            print(stats.full_conversation_size)
