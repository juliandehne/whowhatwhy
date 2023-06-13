from mastodon import Mastodon
from delab_trees import delab_tree
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
    search = mastodon.search(q=query)
    return search

def download_conversations_to_search(query, mastodon):
    search_results = download_search(query=query, mastodon=mastodon)
    statuses = search_results["statuses"]
    conversations = []
    for status in statuses:
        status_id = status["id"]

def find_whole_conversation(status, mastodon):
    conversation_dict = {}
    return conversation_dict

def save_toots_as_tree(status, mastodon):
    conversation = find_whole_conversation(status, mastodon)
    conversation_df = pd.DataFrame(conversation)
    tree = delab_tree.DelabTree(conversation_df)

    


