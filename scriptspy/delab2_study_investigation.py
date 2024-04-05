#%%

import pandas as pd

df = pd.read_csv("~/Dropbox/Projekte/DeLab/Data/delab2_results.csv")

df  = df.drop(columns=["moderation_type"])

#%%

df.needs_moderation.value_counts()
#%%

df2 = df[["text", "flow_name", "create_at"]]

#%%
print(df.needs_moderation.value_counts())

#%%
print(df.sent.value_counts())

#%%
print(df.sendable.value_counts())


#%%

df_intervention = pd.read_csv("~/Dropbox/Projekte/DeLab/backup/020424/postgres_public_mt_study_intervention.csv")
print(df_intervention.sendable.value_counts())
print(df_intervention.sent.value_counts())

#%%

df_classification = pd.read_csv("~/Dropbox/Projekte/DeLab/backup/020424/postgres_public_mt_study_classification.csv")
print(df_classification.needs_moderation.value_counts(dropna=False))