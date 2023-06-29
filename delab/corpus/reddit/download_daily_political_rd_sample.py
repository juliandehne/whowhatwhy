from random import choice

from delab.corpus.reddit.download_conversations_reddit import sort_comments_for_db, compute_reddit_tree
from delab.tw_connection_util import get_praw
from delab_trees.delab_tree import DelabTree
from django_project.settings import MAX_CONVERSATION_LENGTH_REDDIT, MIN_CONVERSATION_LENGTH

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
    "Science",
    "Technology",
    "space",
    "cryptocurrency",
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
    "NetNeutrality",
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
    "PoliticalHumor",
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
    "TrueReddit",
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
    reddit = get_praw()
    subreddit_string = choice(subreddits)
    # could use .hot()
    for submission in reddit.subreddit(subreddit_string).top(time_filter='day'):
        if MAX_CONVERSATION_LENGTH_REDDIT < submission.num_comments < MIN_CONVERSATION_LENGTH:
            continue
        # print(submission)
        comments = sort_comments_for_db(submission)
        comment_dict, root = compute_reddit_tree(comments, submission)
        # print("Found Tree With: ", root.flat_size())
        # print("N_trees_found:", len(result))
        # print(root.to_string())
        if root.compute_max_path_length() > 4:
            tree = DelabTree.from_recursive_tree(root)
            tree.validate(verbose=True)
            result.append(tree)
        if len(result) >= max_results:
            break
    return result
