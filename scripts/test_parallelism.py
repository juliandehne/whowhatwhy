from delab.corpus.reddit.download_daily_political_rd_sample import RD_Sampler
from delab.delab_enums import LANGUAGE


def run():
    sampler = RD_Sampler(language=LANGUAGE.ENGLISH)
    print(sampler.subreddit_string)
    print("en_subreddits", len(RD_Sampler.subreddits))
    print("de_subreddits", len(RD_Sampler.german_political_subreddits))

    sampler2 = RD_Sampler(language=LANGUAGE.GERMAN)
    print(sampler2.subreddit_string)
    print("en_subreddits", len(RD_Sampler.subreddits))
    print("de_subreddits", len(RD_Sampler.german_political_subreddits))

    RD_Sampler.daily_en_subreddits = {}
    RD_Sampler.daily_de_subreddits = {}

    sampler3 = RD_Sampler(language=LANGUAGE.ENGLISH)
    print(sampler3.subreddit_string)
    print("en_subreddits", len(RD_Sampler.subreddits))
    print("de_subreddits", len(RD_Sampler.german_political_subreddits))

    sampler4 = RD_Sampler(language=LANGUAGE.GERMAN)
    print(sampler4.subreddit_string)
    print("en_subreddits", len(RD_Sampler.subreddits))
    print("de_subreddits", len(RD_Sampler.german_political_subreddits))

