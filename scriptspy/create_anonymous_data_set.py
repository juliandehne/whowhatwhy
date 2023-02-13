import pandas as pd
import psycopg2 as pg
import pandas.io.sql as psql
import uuid

connection = pg.connect("host=localhost dbname=postgres user=postgres password=postgres")
query = "SELECT conversation_id as tree_id, id as post_id, tn_parent_id as parent_id," \
        " author_id, created_at, text, platform, sentiment_value, toxic_value" \
        " from delab_tweet"

# from delab_tweet where sentiment_value is not NULL and toxic_value is not NULL" \


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
id_dict = {}
for df_trees_chunk in read_chunks(connection, chunk_size):
    # df_trees = psql.read_sql(query, connection)
    try:
        if df_trees_chunk.empty is False:
            post_ids = df_trees_chunk.post_id
            parent_ids = df_trees_chunk.parent_id
            id_dict_tmp2 = dict([(post_id, uuid.uuid1(post_id)) for post_id in parent_ids])
            id_dict_tmp = dict([(post_id, uuid.uuid1(post_id)) for post_id in post_ids])
            for key, value in id_dict_tmp.items():
                if key not in id_dict:
                    id_dict[key] = value
            for key, value in id_dict_tmp2.items():
                if key not in id_dict:
                    id_dict[key] = value
            # print("processed {} chunks".format(counter))
            chunk = replace_values(df_trees_chunk, id_dict)
            result = pd.concat([result, chunk], ignore_index=True)
    except NameError:
        pass

print("replaced ids with anonymous alternatives")

result['text'] = result['text'].apply(len)

df_trees_twitter = result[result["platform"] == "twitter"]
df_trees_twitter.to_pickle("dataset_twitter_no_text.pkl")

df_trees_reddit = result[result["platform"] == "reddit"]
df_trees_reddit.to_pickle("dataset_reddit_no_text.pkl")

print("created_anonymous datasets with sentiment values")
