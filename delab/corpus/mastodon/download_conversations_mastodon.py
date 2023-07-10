from mastodon import Mastodon
from delab.corpus.DelabTreeDAO import persist_tree, set_up_topic_and_simple_request
from delab_trees.delab_tree import DelabTree
from bs4 import BeautifulSoup
from delab.delab_enums import PLATFORM
import yaml
import pandas as pd


def download_conversations_mstd(query, topic, since=None):
    mastodon = create()
    download_conversations_to_search(query=query, mastodon=mastodon, topic=topic, since=since)


def create():
    """
    You have to register your application in the mastodon web app first,
    (home/preferences/Development/new application)
    then save the necessary information in the file that is called
    """

    with open("twitter/secret/secret_mstd.yaml", 'r') as f:
        access = yaml.safe_load(f)

    mastodon = Mastodon(client_id=access["client_id"],
                        client_secret=access["client_secret"],
                        access_token=access["access_token"],
                        api_base_url="https://mastodon.social/"
                        )
    return mastodon


def download_conversations_to_search(query, mastodon, topic, since):
    statuses = download_timeline(query=query, mastodon=mastodon, since=since)
    contexts = []
    for status in statuses:
        if status in contexts:
            continue
        else:
            context = find_context(status, mastodon)
            contexts.append(context)
    for context in contexts:
        conversation_id = get_conversation_id(context)
        save_toots_as_tree(context=context, topic=topic, query=query, conversation_id=conversation_id)


def download_timeline(query, mastodon, since):
    timeline = mastodon.timeline_hashtag(hashtag=query, limit=40, since_id=since)
    return timeline


def find_context(status, mastodon):
    context = {'origin': status}
    context.update(mastodon.status_context(status["id"]))
    return context


def get_conversation_id(context):
    # mastodon api has no option to get conversation_id by status --> using id of root toot as conversation_id
    ancestors = context["ancestors"]
    origin = context["origin"]
    if origin["in_reply_to_id"] is None:
        return context["origin"]["id"]
    else:
        for status in ancestors:
            if status["in_reply_to_id"] is None:
                return status["id"]


def get_root(context):
    ancestors = context["ancestors"]
    origin = context["origin"]
    if origin["in_reply_to_id"] is None:
        return origin
    for toot in ancestors:
        if toot["in_reply_to_id"] is None:
            return toot
        else:
            raise ValueError("Conversation has no root!")


def save_toots_as_tree(context, conversation_id, topic, query):
    origin = context["origin"]
    descendants = context["descendants"]
    ancestors = context["ancestors"]  # should be emtpy

    tree_context = []
    text = content_to_text(origin["content"])
    tree_status = {'tree_id': conversation_id,
                   'post_id': origin['id'],
                   'parent_id': origin['in_reply_to_id'],
                   'text': text,
                   'created_at': origin['created_at'],
                   'author_id': origin['account']['id'],
                   'lang': origin["language"]}
    tree_context.append(tree_status)
    for status in ancestors:
        text = content_to_text(status["content"])
        tree_status = {'tree_id': conversation_id,
                       'post_id': status['id'],
                       'parent_id': status['in_reply_to_id'],
                       'text': text,
                       'created_at': status['created_at'],
                       'author_id': status['account']['id'],
                       'lang': status["language"]}
        tree_context.append(tree_status)
    for status in descendants:
        text = content_to_text(status["content"])
        tree_status = {'tree_id': conversation_id,
                       'post_id': status['id'],
                       'parent_id': status['in_reply_to_id'],
                       'text': text,
                       'created_at': status['created_at'],
                       'author_id': status['account']['id'],
                       'lang': status["language"]}
        tree_context.append(tree_status)

    context_df = pd.DataFrame(tree_context)
    tree = DelabTree(context_df)
    simple_request, tw_topic = set_up_topic_and_simple_request(query_string=query, request_id=-1, topic_string=topic)
    persist_tree(tree=tree, platform=PLATFORM.MASTODON, simple_request=simple_request, topic=tw_topic)


def content_to_text(content):
    # content is html string --> get only necessary text
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    return text
