import logging
from random import choice

import prawcore

from delab.corpus.DelabTreeDAO import set_up_topic_and_simple_request, check_general_tree_requirements
from delab.corpus.reddit.download_conversations_reddit import sort_comments_for_db, compute_reddit_tree, \
    save_reddit_tree
from delab.delab_enums import LANGUAGE
from delab.tw_connection_util import get_praw
from delab_trees.delab_tree import DelabTree
from django_project.settings import MAX_CONVERSATION_LENGTH_REDDIT, MIN_CONVERSATION_LENGTH

logger = logging.getLogger(__name__)



subreddits = [
    "politics",
    "worldpolitics",
    "geopolitics",
    "politicaldiscussion",
    "PoliticalHumor",
    "Libertarian",
    "socialism",
    "conservative",
    "Liberal",
    "progressive",
    "democrats",
    "republicans",
    "GreenParty",
    "PoliticalRevolution",
    "PoliticalScience",
    "PoliticalPhilosophy",
    "NeutralPolitics",
    "PoliticalCartoons",
    "PoliticalCompass",
    "PoliticalHumor",
    "Ask_Politics",
    "Economics",
    "uspolitics",
    "Anarchism",
    "PoliticalHumor",
    "worldnews",
    "news",
    "usnews",
    "TrueReddit",
    "NeutralNews",
    "moderatepolitics",
    "UKPolitics",
    "CanadaPolitics",
    "Europe",
    "Asia",
    "Africa",
    "MiddleEastNews",
    "LatinAmerica",
    "Australia",
    "RussiaLago",
    "Brexit",
    "The_Mueller",
    "BlackLivesMatter",
    "Feminism",
    "LGBT",
    "climate",
    "environment",
    "ElectionReform",
    "GunPolitics",
    "Healthcare",
    "Education",
    "Labor",
    "Immigration",
    "ForeignPolicy",
    "Military",
    "Justice",
    "CivilRights",
    "Corruption",
    "Privacy",
    "ElectionFraud",
    "PoliticalHumor",
    "PropagandaPosters",
    "Wikileaks",
    "ChangeMyView",
    "Debate",
    "Ask_Politics",
    "PoliticalDiscussion",
    "PoliticalOpinions",
    "WorldPolitics",
    "GlobalTalk",
    "IRstudies",
    "Geopolitics",
    "PoliticalScience",
    "InternationalPolitics",
    "AmericanPolitics",
    "USPolitics",
    "UKPolitics",
    "CanadianPolitics",
    "AusPol",
    "EUnews",
    "MiddleEastPolitics",
    "AfricanPolitics",
    "AsiaPolitics",
    "LatinAmericaPolitics",
    "Socialism",
    "Libertarianism",
    "Conservative",
    "Anarchism",
    "Progressive",
    "GreenParty",
    "Republican",
    "Democrat",
    "LabourUK",
    "SocialDemocracy",
    "PoliticalCompass",
    "NeutralPolitics",
    "AskTrumpSupporters",
    "AskALiberal",
    "AskConservatives",
    "PoliticalCartoons",
    "MensRights",
    "Feminism",
    "LGBTnews",
    "ClimateChange",
    "Environment",
    "Economics",
    "Law",
    "TrueCrime",
    "ConstitutionalLaw",
    "InternationalLaw",
    "Civics",
    "PoliticalPhilosophy",
    "PoliticalTheories",
    "PoliticalHistory",
    "WorldNews",
    "News",
    "NeutralNews",
    "UpliftingNews",
    "WorldEvents",
    "InDepthStories",
    "USnews",
    "UKnews",
    "CanadaNews",
    "AustraliaNews",
    "EuropeNews",
    "AsiaNews",
    "AfricaNews",
    "MiddleEastNews",
    "LatinAmericaNews"
]


def download_daily_rd_sample(topic_string, max_results):
    result = []
    try:
        reddit = get_praw()
        subreddit_string = choice(subreddits)
        # could use .hot()
        count = 0
        for submission in reddit.subreddit(subreddit_string).top(time_filter='day'):
            # print(submission)
            root = compute_reddit_tree(submission)
            tree = DelabTree.from_recursive_tree(root)
            useful = check_general_tree_requirements(tree)
            if useful and tree.validate(verbose=False):
                count += 1
                result.append(tree)
            if count > max_results:
                break
    except prawcore.exceptions.NotFound as ex:
        logger.debug(ex, topic_string)
    except prawcore.exceptions.Forbidden as ex:
        logger.debug(ex, topic_string)
    except prawcore.exceptions.Redirect as ex:
        logger.debug(ex, topic_string)
    return result
