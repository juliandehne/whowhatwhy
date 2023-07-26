from mastodon import Mastodon
from delab.corpus.DelabTreeDAO import persist_tree, set_up_topic_and_simple_request, check_general_tree_requirements
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


def download_conversations_to_search(query, mastodon, topic, since, daily_sample=False):
    statuses = download_timeline(query=query, mastodon=mastodon, since=since)
    contexts = []
    trees = []
    for status in statuses:
        if status in contexts:
            continue
        else:
            context = find_context(status, mastodon)
            if context is None:
                continue
            contexts.append(context)
    for context in contexts:
        conversation_id = context['root']["id"]
        tree = toots_to_tree(context=context, conversation_id=conversation_id)
        if tree is not None:
            trees.append(tree)
            if not daily_sample:
                save_tree_to_db(tree=tree, topic=topic, query=query)

    return trees


def download_timeline(query, mastodon, since):
    timeline = mastodon.timeline_hashtag(hashtag=query, limit=40, since_id=since)
    return timeline


def find_context(status, mastodon):
    context = {'root': status}
    if status['in_reply_to_id'] is None:
        context.update(mastodon.status_context(status["id"]))
    else:
        original_context = {'origin': status}
        original_context.update(mastodon.status_context(status["id"]))
        root = get_root(original_context)
        if root is None:
            return None
        context['root'] = root
        context.update(mastodon.status_context(root["id"]))
    return context


def get_conversation_id(context):
    # mastodon api has no option to get conversation_id by status --> using id of root toot as conversation_id
    ancestors = context["ancestors"]
    origin = context["root"]
    if origin["in_reply_to_id"] is None:
        return context["origin"]["id"]
    else:
        for status in ancestors:
            if status["in_reply_to_id"] is None:
                return status["id"]


def get_root(context):
    ancestors = context["ancestors"]
    origin = context["origin"]
    if origin["in_reply_to_id"] is not None and len(ancestors) == 0:
        print("Conversation has no root!")
        return None
    for toot in ancestors:
        if toot["in_reply_to_id"] is None:
            return toot
    print("Couldn't find root!")
    return None


def toots_to_tree(context, conversation_id):
    root = context["root"]
    descendants = context["descendants"]
    ancestors = context["ancestors"]  # should be emtpy

    tree_context = []
    text = content_to_text(root["content"])
    tree_status = {'tree_id': conversation_id,
                   'post_id': str(root['id']),
                   'parent_id': str(root['in_reply_to_id']),
                   'text': text,
                   'created_at': root['created_at'],
                   'author_id': root['account']['id'],
                   'lang': root["language"]}
    tree_context.append(tree_status)
    for ancestor in ancestors:
        text = content_to_text(ancestor["content"])
        tree_status = {'tree_id': conversation_id,
                       'post_id': str(ancestor['id']),
                       'parent_id': str(ancestor['in_reply_to_id']),
                       'text': text,
                       'created_at': ancestor['created_at'],
                       'author_id': ancestor['account']['id'],
                       'lang': ancestor["language"]}
        tree_context.append(tree_status)
    for descendant in descendants:
        text = content_to_text(descendant["content"])
        tree_status = {'tree_id': conversation_id,
                       'post_id': str(descendant['id']),
                       'parent_id': str(descendant['in_reply_to_id']),
                       'text': text,
                       'created_at': descendant['created_at'],
                       'author_id': descendant['account']['id'],
                       'lang': descendant["language"]}
        tree_context.append(tree_status)

    context_df = pd.DataFrame(tree_context)
    #context_df_clean = pre_process_df(context_df)
    tree = DelabTree(context_df)
    if not check_general_tree_requirements(delab_tree=tree, platform=PLATFORM.MASTODON):
        return None
    return tree


def pre_process_df(context_df):
    """
    convert float and int ids to str
    :return:
    """
    if context_df["parent_id"].dtype != "object":
        df_parent_view = context_df.loc[:, "parent_id"]
        context_df.loc[:, "parent_id"] = df_parent_view.astype(float).astype(str)
    if context_df["post_id"].dtype != "object":
        df_post_view = context_df.loc[:, "post_id"]
        context_df.loc[:, "post_id"] = df_post_view.astype(float).astype(str)
    else:
        assert context_df["parent_id"].dtype == "object" and context_df[
            "post_id"].dtype == "object", "post_id and parent_id need to be both float or str"
    return context_df


def save_tree_to_db(tree, topic, query):
    simple_request, tw_topic = set_up_topic_and_simple_request(query_string=query, request_id=-1, topic_string=topic)
    persist_tree(tree=tree, platform=PLATFORM.MASTODON, simple_request=simple_request, topic=tw_topic)


def content_to_text(content):
    # content is html string --> get only necessary text
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    return text
