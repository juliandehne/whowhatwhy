from mastodon import Mastodon
# from delab_trees import TreeManager
from delab.corpus.twitter.download_conversations_twitter import save_tree_to_db
from util.sql_switch import get_query_native
from delab_trees.delab_tree import DelabTree
from delab.models import Tweet
from delab.delab_enums import PLATFORM
import yaml
import pandas as pd


def download_conversations_mstd(query, topic):
    mastodon = create()
    download_conversations_to_search(query=query, mastodon=mastodon, topic=topic)


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


def download_conversations_to_search(query, mastodon, topic):
    statuses = download_timeline(query=query, mastodon=mastodon)
    contexts = []
    for status in statuses:
        if status in contexts:
            continue
        else:
            context = find_context(status, mastodon)
            contexts.append(context)
    for context in contexts:
        conversation_id = get_conversation_id(context)
        save_toots_as_tweets(context, conversation_id)
        save_toots_as_tree(context=context, topic=topic, query=query, conversation_id=conversation_id)


def download_timeline(query, mastodon):
    timeline = mastodon.timeline_hashtag(hashtag=query, limit=40)
    return timeline


def find_context(status, mastodon):
    context = {'origin': status}
    context.update(mastodon.status_context(status["id"]))
    return context


def get_conversation_id(context):
    # mastodon api has no option to get conversation_id by status --> using id of parent toot as conversation_id
    ancestors = context["ancestors"]
    origin = context["origin"]
    if origin["in_reply_to_id"] is None:
        return context["origin"]["id"]
    else:
        for status in ancestors:
            if status["in_reply_to_id"] is None:
                return status["id"]


def save_toots_as_tweets(context, conversation_id):
    descendants = context["descendants"]
    ancestors = context["ancestors"]
    origin = context["origin"]
    root = get_root(context)
    #toots_in_db = toot_ids_in_db()
    for toot in ancestors:
        tweet = Tweet(twitter_id=toot["id"],
                      text=toot["content"],
                      author_id=toot["account"]["id"],
                      in_reply_to_status_id=toot["in_reply_to_id"],
                      in_reply_to_user_id=toot["in_reply_to_account_id"],
                      created_at=toot["created_at"],
                      conversation_id=conversation_id,
                      tn_original_parent=root["id"],
                      platform=PLATFORM.MASTODON,
                      language=toot["language"],
                      simple_request_id=1,
                      topic_id=2)
        #if toot["id"] not in toots_in_db:
        #tweet.save()
    for toot in descendants:
        tweet = Tweet(twitter_id=toot["id"],
                      text=toot["content"],
                      author_id=toot["account"]["id"],
                      in_reply_to_status_id=toot["in_reply_to_id"],
                      in_reply_to_user_id=toot["in_reply_to_account_id"],
                      created_at=toot["created_at"],
                      conversation_id=conversation_id,
                      tn_original_parent=root["id"],
                      platform=PLATFORM.MASTODON,
                      language=toot["language"],
                      simple_request_id=1,
                      topic_id=2)
        #if toot["id"] not in toots_in_db:
        #tweet.save()
    tweet = Tweet(twitter_id=origin["id"],
                  text=origin["content"],
                  author_id=origin["account"]["id"],
                  in_reply_to_status_id=origin["in_reply_to_id"],
                  in_reply_to_user_id=origin["in_reply_to_account_id"],
                  created_at=origin["created_at"],
                  conversation_id=conversation_id,
                  tn_original_parent=root["id"],
                  platform=PLATFORM.MASTODON,
                  language=origin["language"],
                  simple_request_id=1,
                  topic_id=2)
    #if origin["id"] not in toots_in_db:
    #tweet.save()


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
    tree_status = {'tree_id': conversation_id,
                   'post_id': origin['id'],
                   'parent_id': origin['in_reply_to_id'],
                   'text': origin['content'],
                   'created_at': origin['created_at'],
                   'author_id': origin['account']['id']}
    tree_context.append(tree_status)
    for status in ancestors:
        tree_status = {'tree_id': conversation_id,
                       'post_id': status['id'],
                       'parent_id': status['in_reply_to_id'],
                       'text': status['content'],
                       'created_at': status['created_at'],
                       'author_id': status['account']['id']}
        tree_context.append(tree_status)
    for status in descendants:
        tree_status = {'tree_id': conversation_id,
                       'post_id': status['id'],
                       'parent_id': status['in_reply_to_id'],
                       'text': status['content'],
                       'created_at': status['created_at'],
                       'author_id': status['account']['id']}
        tree_context.append(tree_status)

    context_df = pd.DataFrame(tree_context)
    tree = DelabTree(context_df)
    recursive_tree = tree.as_recursive_tree()
    save_tree_to_db(root_node=recursive_tree, topic=topic, platform=PLATFORM.MASTODON, simple_request=query,
                    conversation_id=conversation_id)
    # return tree
