import logging

from delab.api.api_util import get_all_conversation_ids
from delab.corpus.filter_sequences import get_conversation_flows
from delab.models import ConversationFlow, Tweet
from django_project.settings import MAX_CANDIDATES_DUO_FLOW_ANALYSIS, MAX_DUO_FLOWS_FOR_ANALYSIS
from delab.delab_enums import DUOFLOW_METRIC

logger = logging.getLogger(__name__)

# settings concerning filtering flows
min_length_flows = 6
min_post_branching = 3
min_pre_branching = 3


class FLowDuo:
    def __init__(self, name1, name2, toxic_delta, tweets1, tweets2):
        self.name1 = name1
        self.name2 = name2
        self.toxic_delta = toxic_delta
        self.tweets1: list[Tweet] = tweets1
        self.tweets2: list[Tweet] = tweets2


class FlowDuoWindow(FLowDuo):
    def __init__(self, name1, name2, toxic_delta, tweets1, tweets2, post_branch_length, pre_branch_length):
        super().__init__(name1, name2, toxic_delta, tweets1, tweets2)
        self.common_tweets: list[Tweet] = []
        self.id2tweet = {}
        self.tweets1_post_branching: list[Tweet] = []
        self.tweets2_post_branching: list[Tweet] = []
        self.initialize_window(post_branch_length, pre_branch_length)

    def to_str(self):
        result = ""
        result += "DuoFlows: {} {} with toxic_delta".format(self.name1, self.name2, self.toxic_delta)
        result += "\n\n"
        result += "\n\n"
        result += "Common Tweets:"
        result += "\n\n"
        for common_tweet in self.common_tweets:
            result += common_tweet.text
        result += "\n\n"
        result += "\n\n"
        result += "post-branching tweets flow 1:"
        result += "\n\n"
        for tweet in self.tweets1_post_branching:
            result += tweet.text
        result += "\n\n"
        result += "\n\n"
        result += "post-branching tweets flow 2:"
        result += "\n"
        for tweet in self.tweets2_post_branching:
            result += tweet.text
        return result

    def initialize_window(self, post_branch_length, pre_branch_length):
        self.tweets1 = sorted(list(self.tweets1), key=lambda x: x.created_at)
        self.tweets2 = sorted(list(self.tweets2), key=lambda x: x.created_at)
        flow_1_ids = []
        flow_2_ids = []
        # convert tweet lists to id lists
        for tweet in self.tweets1:
            self.id2tweet[tweet.twitter_id] = tweet
            flow_1_ids.append(tweet.twitter_id)
        for tweet in self.tweets2:
            self.id2tweet[tweet.twitter_id] = tweet
            flow_2_ids.append(tweet.twitter_id)
        intersection_ids: list = set(flow_1_ids).intersection(set(flow_2_ids))
        branching_index = max([flow_2_ids.index(intersect_id) for intersect_id in intersection_ids])
        intersection_id = flow_1_ids[branching_index]
        for tweet in self.tweets1:
            if tweet.twitter_id != intersection_id:
                self.common_tweets.append(tweet)
            else:
                break
        assert flow_2_ids.index(
            intersection_id) == branching_index, "the branching index should be the same for both branches"
        start_index_pre_branching = max(branching_index - pre_branch_length, 0)
        self.common_tweets = self.common_tweets[start_index_pre_branching:branching_index]
        end_index_post_branching = min(branching_index + 1 + post_branch_length, len(self.tweets1), len(self.tweets2))
        self.tweets1_post_branching = self.tweets1[branching_index + 1: end_index_post_branching]
        self.tweets2_post_branching = self.tweets2[branching_index + 1: end_index_post_branching]


def get_flow_duos(n, metric=DUOFLOW_METRIC.TOXICITY):
    """
    # isolate interesting structure one tweet before the branching, the last common tweet between both flows
    # and the following two tweets within the flows.
    @param n number of best flow duos, that have the biggest delta
        @param metric:
    @return [FLowDuo]
    """
    # constraints

    flow_duos = compute_flow_duos(min_length_flows, min_post_branching, min_pre_branching, metric)
    flow_duo_pairs = sorted(flow_duos.keys(), key=lambda x: flow_duos[x])
    result = []
    for name1, name2 in flow_duo_pairs[:n]:
        tweets1 = ConversationFlow.objects.filter(flow_name=name1).get().tweets.all()
        tweets2 = ConversationFlow.objects.filter(flow_name=name2).get().tweets.all()
        flow_duo_result = FLowDuo(
            name1=name1,
            name2=name2,
            toxic_delta=flow_duos[(name1, name2)],
            tweets1=tweets1,
            tweets2=tweets2
        )
        result.append(flow_duo_result)
    return result


def compute_flow_duos(min_length_flows, min_post_branching, min_pre_branching, metric,
                      n_conversation_candidates=MAX_CANDIDATES_DUO_FLOW_ANALYSIS, verbose=False):
    """
    This filters suitable duos of flows in the same conversation that share a  common reply chain but then branch out
    into one branch that is toxic and another that is not. The toxicity is computed by the perspectives api.
    The toxicity columns in the tweet table need to be filled for this to make sense.
    @param min_length_flows:
    @param min_post_branching:
    @param min_pre_branching:
    @param metric: instance of DUOFLOW_METRIC ("sentiment" or "toxicity")
    @param n_conversation_candidates: the number of conversations that looked at as candidates
    @return {(name, name2) -> toxic_delta}
    """
    max_delta = 0
    flow_duos = {}
    conversation_ids = get_all_conversation_ids()
    if metric == DUOFLOW_METRIC.TOXICITY:
        computed_sentiment_filter = {"toxic_value__isnull": False, 'is_toxic': True}
    else:
        computed_sentiment_filter = {"sentiment_value__isnull": False, "sentiment": 'negative'}
    has_toxic_tweet_conversation_ids = set(
        Tweet.objects.filter(**computed_sentiment_filter).values_list("conversation_id", flat=True).all())
    # making sure that some of the sentiment/toxicity has been computed
    conversation_ids = list(set(conversation_ids).intersection(has_toxic_tweet_conversation_ids))
    n_conversation_candidates = min(len(conversation_ids), n_conversation_candidates)
    conversation_ids = conversation_ids[:n_conversation_candidates]
    conversation_count = 0
    for conversation_id in conversation_ids:
        conversation_count += 1
        logger.debug("processed {}/{} conversations".format(conversation_count, len(conversation_ids)))
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
                    if n_pre_branching < min_pre_branching or (n_smaller_flow - n_pre_branching) < min_post_branching:
                        continue
                    else:
                        pos_toxicity = 0
                        for positive_tweet in tweets:
                            if metric == DUOFLOW_METRIC.TOXICITY:
                                if positive_tweet.is_toxic and verbose:
                                    print("adding a toxic value on plus")
                                if positive_tweet.toxic_value is not None:
                                    pos_toxicity += positive_tweet.toxic_value
                            else:
                                if positive_tweet.sentiment_value is not None:
                                    pos_toxicity += positive_tweet.sentiment_value
                        pos_toxicity = pos_toxicity / len(tweets)

                        neg_toxicity = 0
                        for neg_tweet in tweets_2:
                            if metric == DUOFLOW_METRIC.TOXICITY:
                                if neg_tweet.is_toxic and verbose:
                                    print("adding a toxic value on minus")
                                if neg_tweet.toxic_value is not None:
                                    neg_toxicity += neg_tweet.toxic_value
                            else:
                                if neg_tweet.sentiment_value is not None:
                                    neg_toxicity += neg_tweet.sentiment_value
                        neg_toxicity = neg_toxicity / len(tweets_2)

                        if metric == DUOFLOW_METRIC.TOXICITY:
                            tox_delta = abs(pos_toxicity - neg_toxicity)
                        else:
                            tox_delta = 0
                            if (pos_toxicity <= 0 and neg_toxicity <= 0) or (pos_toxicity >= 0 and neg_toxicity >= 0):
                                tox_delta = abs(abs(pos_toxicity) - abs(neg_toxicity))
                            else:
                                if pos_toxicity >= 0 >= neg_toxicity:
                                    tox_delta = pos_toxicity + abs(neg_toxicity)
                                if neg_toxicity >= 0 >= pos_toxicity:
                                    tox_delta = neg_toxicity + abs(pos_toxicity)
                        max_delta = max(max_delta, tox_delta)
                        flow_duos[(name, name_2)] = tox_delta
                        # print("current_highest_delta is {}, after processing acceptable {} flowduos".format(max_delta,
                        #                                                                                    len(flow_duos)))
    logger.debug(
        "current_highest_delta is {}, after processing acceptable {} flowduos".format(max_delta, len(flow_duos)))
    return flow_duos


def flow_duos2flow_windows(dual_flows, post_branch_length=5, pre_branch_length=5):
    result = []
    for dual_flow in dual_flows:
        window = FlowDuoWindow(dual_flow.name1, dual_flow.name2, dual_flow.toxic_delta, dual_flow.tweets1,
                               dual_flow.tweets2, post_branch_length, pre_branch_length)
        result.append(window)
    return result


def get_flow_duo_windows(metric=DUOFLOW_METRIC.SENTIMENT):
    dual_flows = get_flow_duos(MAX_DUO_FLOWS_FOR_ANALYSIS, metric)
    result = flow_duos2flow_windows(dual_flows)
    return result
