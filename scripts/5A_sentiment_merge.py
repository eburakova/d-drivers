import os
import warnings
import pandas as pd
from tqdm import tqdm

df_features = pd.read_csv('data/data_features.csv')
df_nlp = pd.read_csv('data/data_nlp.csv', usecols=['page_id','sentiment_abstract','confidence_abstract','sentiment_meta_title','confidence_meta_title'])

df = pd.merge(df_features, df_nlp, on='page_id', how='outer') # doing outer to make failures be visible if there are any problems with the data
df.to_csv('data/data_nlp_A.csv', encoding='utf-8', index=False)
print('The full dataframe with features is saved as data/data_nlp_A.csv')

print('======== Processing complete ========')