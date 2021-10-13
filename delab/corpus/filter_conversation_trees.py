import pandas as pd
from django_pandas.io import read_frame

from delab.TwConversationTree import TreeNode
from delab.models import Tweet
from util.sql_switch import query_sql


def get_standard_field_names():
    return ["id",
            "conversation_id",
            "author_id",
            "created_at",
            "in_reply_to_user_id",
            "text"]


def filter_conversations(max_orphan_count=4, min_depth=3, merge_subsequent=True, fieldnames=None):
    # a utility so I don't have to rewrite the get twitter corpus for both django and jupyter context
    if fieldnames is None:
        fieldnames = get_standard_field_names()

    df = query_sql(
        fieldnames=fieldnames)

    return crop_trees(df, max_orphan_count, min_depth, merge_subsequent)


def get_filtered_conversations(conversation_id, max_orphan_count=4, min_depth=3, merge_subsequent=True, fieldnames=None):
    # rewrite this for the query_sql-utility
    if fieldnames is None:
        fieldnames = get_standard_field_names()

    qs = Tweet.objects.filter(conversation_id=conversation_id).all()
    df = read_frame(qs, fieldnames=fieldnames)

    return crop_trees(df, max_orphan_count, min_depth, merge_subsequent)


def crop_trees(df, max_orphan_count=4, min_depth=3, merge_subsequent=True):
    '''

    :param merge_subsequent: Boolean merge subsequent tweets from same authors
    :param df: the dataframe containing a tweet per row
    :param max_orphan_count: the max number the trees are allowed to branch
    :param min_depth: the minimal number of answers to answers in a tree
    :return: useful_trees, ids: ([TreeNode], [int])
    '''
    if merge_subsequent:
        df = merge_subsequent_tweets(df)

    roots = df[df["in_reply_to_user_id"].isnull()]
    not_roots = df[df["in_reply_to_user_id"].notnull()]
    # print(not_roots.shape)
    roots_as_rec = roots.to_dict('records')
    not_roots_as_rec = not_roots.to_dict('records')
    # roots_as_rec[0:5]
    trees_roots = {}
    for root_data in roots_as_rec:
        root_data["in_reply_to_user_id"] = root_data["author_id"]
        trees_roots[root_data["conversation_id"]] = TreeNode(root_data)  # root is defined as answering to him/herself
    for not_root in not_roots_as_rec:
        if not_root["conversation_id"] in trees_roots:
            trees_roots.get(not_root["conversation_id"]).find_parent_of(TreeNode(not_root))
    # filtering out the trees that are too short
    useful_trees = []
    trees = list(trees_roots.values())
    for tree in trees:
        if tree.get_max_path_length() > min_depth:
            #  print(tree.get_max_path_length())
            useful_trees.append(tree)
    useful_trees_ids = []
    useful_trees_conversation_ids = []
    # useful_number_of_tweets = 0
    for useful_tree in useful_trees:
        useful_tree.crop_orphans(max_orphan_count)
        useful_trees_ids += (useful_tree.all_tweet_ids())
        # TODO why the heck are the integers rounded down at the last two positions!
        useful_trees_conversation_ids.append(useful_tree.data["conversation_id"])
        # useful_number_of_tweets += useful_tree.flat_size()
        # useful_tree.print_tree(0)
    # print("we found {} useful tweets".format(useful_number_of_tweets))
    return useful_trees, useful_trees_ids, useful_trees_conversation_ids


def merge_subsequent_tweets(df):
    fieldnames = get_standard_field_names()
    df.sort_values(by=['conversation_id', 'author_id', "created_at"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    data_list = df.to_dict('records')
    # print("before merging there are {} tweets".format(len(data_list)))
    result = []
    duplicates_ids = []
    for current, next_one in zip(data_list, data_list[1:]):
        if current["id"] not in duplicates_ids:
            if current["author_id"] == next_one["author_id"] \
                    and current["conversation_id"] == next_one["conversation_id"]:
                current["text"] = current["text"] + "<new_tweet><replyto:"
                current["text"] = current["text"] + str(next_one["in_reply_to_user_id"]) + ">" + next_one["text"]
                duplicates_ids.append(next_one["id"])
        result.append(current)
    df = pd.DataFrame(result, columns=fieldnames)
    return df

# https://stackoverflow.com/questions/67454/serving-dynamically-generated-zip-archives-in-django
