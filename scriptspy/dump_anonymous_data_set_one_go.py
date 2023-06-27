import numpy as np
import pandas as pd
import psycopg2 as pg
import pandas.io.sql as psql
import uuid

connection = pg.connect("host=localhost dbname=postgres user=postgres password=postgres")
query = "SELECT conversation_id as tree_id, twitter_id as post_id, tn_parent_id as parent_id," \
        " author_id, created_at, text, platform, sentiment_value, toxic_value" \
        " from delab_tweet"

# from delab_tweet where sentiment_value is not NULL and toxic_value is not NULL" \

result = pd.read_sql(query, connection)

# result['parent_id'] = result['parent_id'].apply(int)

result['post_id'] = result['post_id'].apply(float)
result['tree_id'] = result['tree_id'].apply(float)
result['parent_id'] = result['parent_id'].apply(float)
post_ids = result.post_id
id2anonymous = dict([(post_id, uuid.uuid4()) for post_id in post_ids if post_id])
result['parent_id'] = result['parent_id'].map(id2anonymous)
print("replaced post ids with anonymous alternatives")
result['post_id'] = result['post_id'].map(id2anonymous)
print("replaced parent ids with anonymous alternatives")
result['tree_id'] = result['tree_id'].map(id2anonymous)
result['text'] = result['text'].apply(len)
print("replaced text with anonymous text_length")

df_trees_twitter = result[result["platform"] == "twitter"]
df_trees_twitter.to_pickle("dataset_twitter_no_text.pkl")

df_trees_reddit = result[result["platform"] == "reddit"]
df_trees_reddit.to_pickle("dataset_reddit_no_text.pkl")

print("created_anonymous datasets with sentiment values")
