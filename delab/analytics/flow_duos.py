import logging

from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_sequences import get_conversation_flows
from delab.models import Conversation, ConversationFlow

logger = logging.getLogger(__name__)


class FLowDuo:
    def __init__(self, name1, name2, toxic_delta, tweets1, tweets2):
        self.name1 = name1
        self.name2 = name2
        self.toxic_delta = toxic_delta
        self.tweets1 = tweets1
        self.tweets2 = tweets2


def get_flow_duos(n):
    """
    # isolate interesting structure one tweet before the branching, the last common tweet between both flows
    # and the following two tweets within the flows.
    @param n number of best flow duos, that have the biggest delta
    @return [FLowDuo]
    """
    # constraints
    min_length_flows = 10
    min_post_branching = 5
    min_pre_branching = 3
    max_delta = 0

    flow_duos = compute_flow_duos(max_delta, min_length_flows, min_post_branching, min_pre_branching)
    flow_duo_pairs = sorted(flow_duos.keys(), key=lambda x: flow_duos[x])
    result = []
    for name1, name2 in flow_duo_pairs[:n]:
        tweets1 = ConversationFlow.objects.filter(flow_name=name1).tweet_set
        tweets2 = ConversationFlow.objects.filter(flow_name=name2).tweet_set
        flow_duo_result = FLowDuo(
            name1=name1,
            name2=name2,
            toxic_delta=flow_duos[(name1, name2)],
            tweets1=tweets1,
            tweets2=tweets2
        )
        result.append(flow_duo_result)
    return result


def compute_flow_duos(max_delta, min_length_flows, min_post_branching, min_pre_branching):
    """
    @param max_delta:
    @param min_length_flows:
    @param min_post_branching:
    @param min_pre_branching:
    @return {(name, name2) -> toxic_delta}
    """
    flow_duos = {}
    conversation_ids = get_all_conversation_ids()
    for conversation_id in conversation_ids:
        try:
            flows, longest = get_conversation_flows(conversation_id)
        except AssertionError as ae:
            logger.error(ae)
            continue
        candidate_flows = []
        for name, tweets in flows.items():
            if len(tweets) > min_length_flows:
                continue
            else:
                candidate_flows.append((name, tweets))

        for name, tweets in candidate_flows:
            for name_2, tweets_2 in candidate_flows:
                if name_2 != name:
                    tweet_ids = set([tweet.twitter_id for tweet in tweets])
                    tweet2_ids = set([tweet.twitter_id for tweet in tweets_2])
                    n_pre_branching = len(tweet_ids.intersection(tweet2_ids))
                    n_smaller_flow = min(len(tweet_ids), len(tweet2_ids))
                    if n_pre_branching < min_pre_branching and (n_smaller_flow - n_pre_branching) < min_post_branching:
                        continue
                    else:
                        pos_toxicity = 0
                        for positive_tweet in tweets:
                            pos_toxicity += positive_tweet.toxic_value
                        pos_toxicity = pos_toxicity / len(tweets)

                        neg_toxicity = 0
                        for neg_tweet in tweets:
                            neg_toxicity += neg_tweet.toxic_value
                        neg_toxicity = neg_toxicity / len(tweets_2)
                        tox_delta = pos_toxicity - neg_toxicity
                        max_delta = max(max_delta, tox_delta)
                        flow_duos[(name, name_2)] = tox_delta
                        print("current_highest_delta is {}, after processing acceptable {} flowduos".format(max_delta,
                                                                                                            len(flow_duos)))
    return flow_duos
