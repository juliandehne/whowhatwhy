import pandas as pd

filenames = ['afd_tweet', 'gendern_tweets', 'speech_tweets', 'tempolimit_tweets']

for filename in filenames:
    # Opening JSON file
    # filename = 'gendern_tweets'

    df = pd.read_json('data/' + filename + '.jsonl', lines=True, typ='series')
    # df.head()

    df = pd.json_normalize(df, 'data', errors='ignore')
    df.to_csv(filename + '.csv')
