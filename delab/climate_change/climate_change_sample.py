from delab.corpus.twitter.download_author_information import download_authors
from delab.delab_enums import CLIMATEAUTHOR
from delab.models import ClimateAuthor, TweetAuthor
from delab.tw_connection_util import DelabTwarc


def create_climate_authors(data, lang):
    accounts = []
    for key in data:
        data2 = data[key]
        for key2 in data2:
            k = list(key2.keys())
            type = k[0]
            for key3 in key2:
                author = key2[key3]
                name = author['name']
                twitter_account = author['twitter_account']
                governmental = False
                if 'governmental' in author.keys():
                    if author['governmental'] == 'true':
                        governmental = True
                elif type == 'politician':
                    governmental = True
                if name == "":
                    continue
                climate_author = ClimateAuthor(type=type, name=name, twitter_account=twitter_account,
                                               governmental=governmental, language=lang)
                if not ClimateAuthor.objects.filter(name=climate_author.name).exists():
                    climate_author.save()
                    accounts.append(twitter_account)
    update_is_climate_author(accounts)
    set_climate_author_type()


def update_is_climate_author(names):
    twarc = DelabTwarc()
    ids = twarc.user_lookup(users=names, usernames=True)
    missing_authors = []
    missing_author_names = []
    for id_batch in ids:
        if "data" in id_batch:
            for author_payload in id_batch["data"]:
                tw_id = author_payload["id"]
                tw_username = author_payload["username"]
                climate_authors = TweetAuthor.objects.filter(twitter_id=tw_id).all()
                if climate_authors.count() == 0:
                    missing_authors.append(tw_id)
                    missing_author_names.append(tw_username)
                for tweetAuthor in climate_authors:
                    tweetAuthor.is_climate_author = True
                    tweetAuthor.save(update_fields=["is_climate_author"])
                download_authors(missing_authors)
                update_is_climate_author(missing_author_names)


def set_climate_author_type():
    climate_authors = TweetAuthor.objects.filter(is_climate_author=True).all()
    for author in climate_authors:
        author_screen_name = author.screen_name
        cl_authors = ClimateAuthor.objects.filter(twitter_account=author_screen_name).all()
        for cl_author in cl_authors:
            author_type = cl_author.type
            if author_type == 'organisation' and not cl_author.governmental:
                author.climate_author_type = CLIMATEAUTHOR.NGO
                author.save()
            else:
                author.climate_author_type = author_type
                author.save()
