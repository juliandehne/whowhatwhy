import pandas as pd
import psycopg2 as pg
import pandas.io.sql as psql
import uuid

connection = pg.connect("host=localhost dbname=postgres user=postgres password=postgres")
query = "SELECT conversation_id as tree_id, id as post_id, tn_parent_id as parent_id, author_id, created_at, text, platform from delab_tweet"


# creating the dictionary


def replace_values(df, replace_dict):
    for col in df.columns:
        df[col].replace(replace_dict, inplace=True)
    return df


def read_chunks(conn, chunk_size):
    cursor = conn.cursor()
    cursor.execute(query)
    colnames = [desc[0] for desc in cursor.description]

    while True:
        try:
            chunk = cursor.fetchmany(chunk_size)
            df = pd.DataFrame(chunk)
            df.columns = colnames
            yield df
        except ValueError:
            break
    yield pd.DataFrame()


print("reading in chunks")
chunk_size = 10000
result = pd.DataFrame()
counter = 0
for df_trees_chunk in read_chunks(connection, chunk_size):
    # df_trees = psql.read_sql(query, connection)
    try:
        if df_trees_chunk.empty is False:
            post_ids = df_trees_chunk.post_id
            id_dict = dict([(post_id, uuid.uuid1(post_id)) for post_id in post_ids])
            # print("processed {} chunks".format(counter))
            chunk = replace_values(df_trees_chunk, id_dict)
            result = pd.concat([result, chunk], ignore_index=True)
    except NameError:
        pass

# df_trees.replace(id_dict, inplace=True)
# cassert len(result.index) > 10000
print("replaced ids with anonymous alternatives")


df_trees_twitter = result[result["platform"] == "twitter"]
df_trees_twitter = df_trees_twitter.drop(["platform", "text"], axis=1)
df_trees_twitter.to_pickle("dataset_twitter_no_text.pkl")

print(df_trees_twitter.head(3))

df_trees_reddit = result[result["platform"] == "reddit"]
df_trees_reddit = df_trees_reddit.drop(["platform", "text"], axis=1)
df_trees_reddit.to_pickle("dataset_reddit_no_text.pkl")

print(df_trees_reddit.head(3))
