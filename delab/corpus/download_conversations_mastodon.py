from mastodon import Mastodon
from delab_trees import TreeManager
from delab.models import Tweet
from delab.delab_enums import PLATFORM
import pandas as pd


def download_conversations_mstd(query):
    mastodon = create()
    download_conversations_to_search(query=query, mastodon=mastodon)


def create():
    Mastodon.create_app(
        'pytooterapp',
        api_base_url='https://mastodon.social',
        to_file='pytooter_clientcred.secret'
    )
    # your login credentials have to be in this folder/file as: 'my_login_email@example.com', 'incrediblygoodpassword'
    with open("../mastodon/secret.txt") as f:
        login = f.readlines()

    mastodon = Mastodon(client_id='pytooter_clientcred.secret', )
    mastodon.log_in(
        login,
        to_file='pytooter_usercred.secret'
    )

    return mastodon


def download_search(query, mastodon):
    search = mastodon.search(q=query, type='hashtags')
    return search


def download_conversations_to_search(query, mastodon):
    search_results = download_search(query=query, mastodon=mastodon)
    statuses = search_results["statuses"]
    contexts = []
    for status in statuses:
        if status in contexts:
            continue
        else:
            context = find_context(status, mastodon)
            contexts.append(context)

    for context in contexts:
        conversation_id = get_conversation_id(context, mastodon)
        save_toots_as_tweets(context, conversation_id)
        save_toots_as_tree(context)


def find_context(status, mastodon):
    if status["in_reply_to"] == "null":
        context = {'root': status}
        context.update(mastodon.get_context(status["id"]))
    else:
        status_context = mastodon.get_context(status["id"])
        for status in status_context["ancestors"]:
            if status["in_reply_to"] == "null":
                parent = status
                break
        context = {'root': parent}
        context.update(mastodon.get_context(parent["id"]))
    return context


def get_conversation_id(context, mastodon):
    last_toot = context["descendants"][-1]
    last_toot_id = last_toot["id"]
    conversation = mastodon.conversations(max_id=last_toot_id)
    return conversation["id"]


def save_toots_as_tweets(context, conversation_id):
    toots = context["descendants"]
    root = context["root"]
    for toot in toots:
        tweet = Tweet(twitter_id=toot["id"],
                      text=toot["content"],
                      author_id=toot["account"]["id"],
                      in_reply_to_status_id=toot["in_reply_to_id"],
                      in_reply_to_user_id=toot["in_reply_to_account_id"],
                      created_at=toot["created_at"],
                      conversation_id=conversation_id,
                      tn_original_parent=root["id"],
                      platform=PLATFORM.MASTODON,
                      language=toot["language"])


def save_toots_as_tree(context, conversation_id):
    root = context["root"]
    descendants= context["descendants"]
    ancestors = context["ancestors"] #should be emtpy
    full_context = descendants.append(root)
    full_context = full_context.append(ancestors)
    for status in full_context:
        status['tree_id']=conversation_id
        status['post_id']=status.pop('id')
        status['parent_id'] = status.pop('in_reply_to_account_id')
        status['text'] = status.pop('content')

    context_df = pd.DataFrame(full_context)
    tree_manager = TreeManager(context_df)


