import datetime
import random

from django.contrib.auth.models import User

from delab.corpus.download_conversations import save_tree_to_db
from delab.TwConversationTree import TreeNode
from delab.models import Tweet, TwTopic, SimpleRequest, TWCandidateIntolerance, TWIntoleranceRating
from delab.delab_enums import PLATFORM, LANGUAGE
from delab.nce.download_intolerant_tweets import download_terrible_tweets

"""
The idea is that this script provides a fake conversation to test the labeling pipeline
"""


def run():
    clean = True  # delete old fake data
    create = True  # create new fake data
    rank_them = True  # non-fake data to make it clearer

    topic_string = "fake_conversations"
    # create the topic and save it to the db
    topic, created = TwTopic.objects.get_or_create(
        title=topic_string
    )
    simple_request, created = SimpleRequest.objects.get_or_create(
        title="creating faking conversations",
        topic=topic
    )

    if clean:
        TWCandidateIntolerance.objects.filter(tweet__topic__title=topic_string).delete()
        Tweet.objects.filter(topic__title=topic_string).delete()
        Tweet.objects.filter(topic__title=topic_string).delete()

    if create:
        tree = create_conversation(lang=LANGUAGE.GERMAN)
        # print(tree.to_string())
        tree_en = create_conversation(lang=LANGUAGE.ENGLISH)
        # print(tree.to_string())
        save_tree_to_db(tree_en, topic, simple_request, 1, platform=PLATFORM.DELAB)
        save_tree_to_db(tree, topic, simple_request, 2, platform=PLATFORM.DELAB)
        download_terrible_tweets(False, True)
        # this ranks existing candidates as intolerant in order to have a clear view on the fake ones
    if rank_them:
        rank_them_others()


def rank_them_others():
    candidates = TWCandidateIntolerance.objects.filter(tweet__platform=PLATFORM.TWITTER).all()
    for candidate in candidates:
        TWIntoleranceRating.objects.get_or_create(
            u_person_hate=False,
            candidate=candidate,
            coder=User.objects.filter(username="dehne").get()
        )
        TWIntoleranceRating.objects.create(
            u_person_hate=False,
            candidate=candidate,
            coder=User.objects.filter(username="delab").get()
        )


def create_conversation(lang):
    conversation_id = 1
    conv = twitterconv_en
    if lang == LANGUAGE.GERMAN:
        conversation_id = 2
        conv = twitterconv_de

    root_text = conv[0]
    data = generate_fake_tweet_data(root_text, conversation_id, lang=lang)
    tree = TreeNode(data, data['id'])
    current_tree = None
    for fake_tweet in conv[1:]:
        data = generate_fake_tweet_data(fake_tweet, conversation_id, lang=lang)

        if current_tree is None:
            child = TreeNode(data, data['id'], tree.tree_id)
            tree.children.append(child)
        else:
            child = TreeNode(data, data['id'], current_tree.tree_id)
            current_tree.children.append(child)
        current_tree = child
    return tree


def generate_fake_tweet_data(text, conversation_id=1, lang=LANGUAGE.ENGLISH):
    data = {"text": text,
            "id": abs(hash(text)),
            "author_id": 42,
            "created_at": datetime.datetime.now(),
            "conversation_id": conversation_id,
            "lang": lang
            }
    return data


tweet1 = '>>Warum darf man das wort Zigeuner-Soße eigentlich nicht mehr sagen?'
ans1 = '>>@merle123 weil das z-wort diskriminierent gegenüber Sinti und Roma ist'
ans1_1 = '>>@karin508 früher haben wir einfach gesagt was uns gefällt, da haben sich die scheiß Zigeuner doch auch nicht beschwert!'
ans1_2 = '>>@reinhartt ernsthaft...?'
ans1_3 = '>>@reinhartt bruder halts maul'
ans2 = '>>@merle123 man darf sagen was man will. In diesem Land gilt die Meinungfreiheit! diese linken Spasten wollen und den Mund verbieten!'
ans2_1 = '>>@diana59 isso!'
ans2_2 = '>>@diana59 heul doch.'
ans3 = '>>@merle123 frag ich mich auch! Als ob das irgendeinen Zigeuner juckt, die können doch eh kein deutsch'
ans4 = '>>@merle123 die scheiß zecken wollen doch nur dass wir spuren! lass dir nichts verbieten!'

twitterconv_de = [tweet1, ans1, ans1_1, ans1_2, ans1_3, ans2, ans2_1, ans2_2, ans3, ans4]

tweet1_en = '>>Happy International Day against Homophobia,Transphobia and Biphobia!'
ans1_en = '>>@lauren505 wow! the fags are getting really creative with their days!'
ans1_2_en = '>>@micheal77 for real!'
ans1_3_en = '>>@micheal77 if you dont want to celebrate it, thats fine'
ans2_en = '>>@lauren505 why are dykes always telling everyone they are dykes? i really dont care!'
ans2_1_en = '>>@karennn when did they say they were a lesbian?:D'
ans2_2_en = '>>@karennn i swear the lesbos are getting crazy'
ans3_en = '>>lauren505 yayy we love<3'
ans4_en = '>>lauren505 so everyday is homo day now?'

twitterconv_en = [tweet1_en, ans1_en, ans1_2_en, ans1_3_en, ans2_en, ans2_1_en, ans2_2_en, ans3_en, ans4_en]
