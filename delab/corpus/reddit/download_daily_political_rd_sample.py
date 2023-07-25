import logging
from datetime import datetime
from random import choice
from time import sleep

import prawcore

from delab.corpus.DelabTreeDAO import set_up_topic_and_simple_request, check_general_tree_requirements
from delab.corpus.download_exceptions import NoDailySubredditAvailableException
from delab.corpus.reddit.download_conversations_reddit import sort_comments_for_db, compute_reddit_tree, \
    save_reddit_tree
from delab.delab_enums import LANGUAGE
from delab.tw_connection_util import get_praw
from delab_trees.delab_tree import DelabTree
from django_project.settings import MAX_CONVERSATION_LENGTH_REDDIT, MIN_CONVERSATION_LENGTH

logger = logging.getLogger(__name__)


class RD_Sampler:
    german_political_subreddits = [
        "de_IAmA",
        "de_podcasts",
        "depression_de",
        "finanzen",
        "grundeinkommen",
        "nachrichten",
        "piratenpartei",
        "recht",
        "sozialismus",
        "wissenschaft",
        "afd",
        "antikapitalismus",
        "antinational",
        "bundestag",
        "cdu",
        "die_linke",
        "diepartei",
        "dokumentation",
        "fdp",
        "hartz4",
        "klimawandel",
        "kommunismus",
        "nachhaltigkeit",
        "piraten",
        "spd",
        "wirtschaft",
        "austria",
        "Dachschaden",
        "aeiou",
        "spacefrogs",
        "GeschichtsMaimais",
        "Kaiserposting",
        "600euro",
        "mauerstrassenwetten",

    ]

    subreddits = [
        "protest",
        "migration",
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
        "Refugees",
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
        "LatinAmericaNews",
        "neoliberal",
    ]

    daily_en_subreddits = {}
    daily_de_subreddits = {}

    def __init__(self, language):
        current_date = datetime.now().date()
        # init dictionary of subreddits if empty
        if current_date not in RD_Sampler.daily_en_subreddits:
            RD_Sampler.daily_en_subreddits[current_date] = RD_Sampler.subreddits
        if current_date not in RD_Sampler.daily_de_subreddits:
            RD_Sampler.daily_de_subreddits[current_date] = RD_Sampler.german_political_subreddits
        # get current state of available subreddits and pick one
        if language == LANGUAGE.GERMAN:
            available_reddits = RD_Sampler.daily_de_subreddits[current_date]
        else:
            available_reddits = RD_Sampler.daily_en_subreddits[current_date]
        if len(available_reddits) == 0:
            raise NoDailySubredditAvailableException(language=language)
        else:
            subreddit_string = choice(available_reddits)
        # update dictionary with current available states
        if language == LANGUAGE.ENGLISH:
            current_list = RD_Sampler.daily_en_subreddits[current_date]
            current_list.remove(subreddit_string)
            RD_Sampler.daily_en_subreddits[current_date] = current_list
        else:
            current_list = RD_Sampler.daily_de_subreddits[current_date]
            current_list.remove(subreddit_string)
            RD_Sampler.daily_de_subreddits[current_date] = current_list
        self.subreddit_string = subreddit_string
        logger.debug(
            "current subreddits to search are en: {}, de: {}".format(RD_Sampler.daily_en_subreddits[current_date],
                                                                     RD_Sampler.daily_de_subreddits[current_date]))
        self.language = language
        self.current_date = current_date

    def download_daily_rd_sample(self, max_results):
        result = []
        try:
            reddit = get_praw()

            # could use .hot()
            count = 0
            for submission in reddit.subreddit(self.subreddit_string).top(time_filter='day'):
                # print(submission)
                root = compute_reddit_tree(submission, self.language)
                tree = DelabTree.from_recursive_tree(root)
                # validate tree here so that there are not too many downloads necessary
                useful = check_general_tree_requirements(tree)
                valid = tree.validate(verbose=False)
                if useful and valid:
                    count += 1
                    result.append(tree)
                if count > max_results:
                    break
        except prawcore.exceptions.NotFound as ex:
            logger.debug(ex)
        except prawcore.exceptions.Forbidden as ex:
            logger.debug(ex)
        except prawcore.exceptions.Redirect as ex:
            logger.debug(ex)
        except prawcore.exceptions.TooManyRequests as ex:
            # logger.debug(ex)
            logger.debug("too many requests, going to sleep for 15 min")
            sleep(60 * 15)
        except prawcore.exceptions.ServerError as ex:
            logger.debug(ex)
        logger.debug("returning {} conversations for subreddit {}, {} subreddits not searched for lang {}"
                     .format(len(result), self.subreddit_string, len(self.get_current_dictionary()), self.language))
        return result

    def get_current_dictionary(self):
        if self.language == LANGUAGE.ENGLISH:
            return self.daily_en_subreddits[self.current_date]
        else:
            return self.daily_de_subreddits[self.current_date]
