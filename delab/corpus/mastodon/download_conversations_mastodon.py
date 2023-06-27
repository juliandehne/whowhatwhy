from mastodon import Mastodon
#from delab_trees import TreeManager
from delab.corpus.twitter.download_conversations_twitter import save_tree_to_db
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
        conversation_id = get_conversation_id(context, mastodon)
        save_toots_as_tweets(context, conversation_id)
        save_toots_as_tree(context=context, topic=topic, query=query, conversation_id=conversation_id)


def download_timeline(query, mastodon):
    timeline = mastodon.timeline_hashtag(hashtag=query)
    return timeline


def find_context(status, mastodon):
    context = {'origin': status}
    context.update(mastodon.status_context(status["id"]))
    return context


def get_conversation_id(context, mastodon):
    first_toot_id = context["origin"]["id"]
    conversation = mastodon.conversations(min_id=first_toot_id, limit=1)
    print(conversation)
    return 100 #Platzhalter


def save_toots_as_tweets(context, conversation_id):
    descendants = context["descendants"]
    ancestors = context["ancestors"]
    origin = context["origin"]
    toots = descendants + ancestors + origin
    root = get_root(context)
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


def get_root(context):
    descendants = context["descendants"]
    ancestors = context["ancestors"]
    origin = context["origin"]
    toots = descendants + ancestors + origin
    for toot in toots:
        if toot["in_reply_to_id"] == "null":
            return toot
        else:
            raise ValueError("Conversation has no root!")


def save_toots_as_tree(context, conversation_id, topic, query):
    root = context["origin"]
    descendants = context["descendants"]
    ancestors = context["ancestors"]  # should be emtpy
    full_context = descendants.append(root)
    full_context = full_context.append(ancestors)
    tree_context = []
    for status in full_context:
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
