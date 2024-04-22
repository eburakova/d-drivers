## For explanations see ./notebooks/Cleaning-categorising-katja.ipynb

import pandas as pd

print('======== This is the script that combines and tidies up the raw data ========')
print('The run should take approx. 30 seconds.')
print()
print('Reading the first data delivery...')

# Read part of the malformatted file:
df1 = pd.read_excel('data/data_d-drivers_2024-03-24.xlsx', sheet_name='data',
                    usecols=['PAGE_EFAHRER_ID', 'DATE', 'PAGE_CANONICAL_URL', 'PAGE_AUTHOR', 'WORD_COUNT', 'CLICKOUTS'],
                    #parse_dates=['DATE']
                    )
print('Reading the second data delivery...')
#Read everything from the new file:
df2 = pd.read_excel('data/data_d-drivers_2024-03-26.xlsx', sheet_name='data',
                    #parse_dates=['DATE', 'PUBLISHED_AT']
                    )

print('Reading complete. \nCleaning up the dataframes...')
df1.columns = [col.lower() for col in df1.columns]
df2.columns = [col.lower() for col in df2.columns]

df1.rename({
           #'impressions': 'page_impressions',
           'page_efahrer_id': 'page_id',
           'published_at': 'publish_date',
           'page_canonical_url': 'url',
           'page_author': 'authors', 
            }, axis=1, inplace=True)

df2.rename({
           'impressions': 'page_impressions',
           'page_efahrer_id': 'page_id',
           'published_at': 'publish_date',
           'page_canonical_url': 'url',
           'page_author': 'authors', 
            }, axis=1, inplace=True)

# Eliminate mistakes from the table
df1.drop(78658, inplace=True)
df2.drop(40600, inplace=True)

### Merging ###

# Using the `left` merging: we already know that `df1` is malformatted
key_columns = ['page_id', 'date', 'url', 'authors', 'word_count']

print('Merging...')
df = pd.merge(left=df2, right=df1, on=key_columns, how='left') 

### Imputing ###
print('Imputing...')
df = df.sort_values(['page_id', 'date', 'publish_date', 'url'])\
    .reset_index(drop=False)
df.rename({'index': 'old_index'}, axis=1, inplace=True)

# reshuffling columns
df = df[['old_index', 'page_id', 'date', 'publish_date', 'word_count',
       'publish_date_equal_to_date', # we don't need this one anymore (and never needed?)
       'url', 'page_name', 'classification_product', 'classification_type',
       'title', 'authors', 'daily_likes', 'daily_dislikes', 
       'video_play', 'page_impressions', 'clickouts', 
       'external_clicks', 'external_impressions'
        ]]

# Drop negative and too large likes and dislikes

### Imputing ###

df_imputed = df.copy()## Placeholder

df_imputed = df_imputed.sort_values(['page_id', 'date', 'publish_date']) # just in case, should be already sorted

df_imputed['word_count'] = df_imputed.groupby(['page_id', 'date'])['word_count'].ffill()
df_imputed['word_count'] = df_imputed.groupby(['page_id'])['word_count'].ffill()

# Impute the still missing word counts with 0
# -> In the future: take the value of the `word count (scraped)` 
# or the mean value for the given category! 
df_imputed['word_count'] = df_imputed['word_count'].fillna(0)

df_imputed['publish_date'] = df_imputed.groupby(['page_id', 'date'])['publish_date'].ffill()
df_imputed['publish_date'] = df_imputed.groupby(['page_id'])['publish_date'].ffill()
df_imputed['publish_date'] = df_imputed['publish_date'].fillna(pd.Timestamp('2018-01-01 00:00'))
# df_imputed.loc[df_imputed.publish_date != df_imputed.date] = min(df_imputed.publish_date, df_imputed.date)

### Drop the articles with no metrics at all (enough to check external_clicks)
### As well as the rows with no targets

df_imputed = df_imputed[df_imputed.external_clicks.notna()]

# -> Comment the line above and uncomment THIS SNIPPET BELOW 
# to drop ONLY the articles with no metrics AT ALL #####
#
# df_imputed['missing_external'] = df_imputed.external_clicks.isna()
# page_ids_to_drop = (df_imputed[['page_id', 'missing_external']]\
#                .groupby('page_id', as_index=False)).all()
# page_ids_to_drop = page_ids_to_drop[page_ids_to_drop.missing_external].page_id.unique()

# print(f'Dropped {len(page_ids_to_drop)} unique articles')
# # Should drop 49 articles 
# df_imputed = df_imputed[~df_imputed.page_id.isin(page_ids_to_drop)]
# 
# ----------------------------------------------------------

### Dropping the articles which are not online anymore
# See Scraping-katja.ipynb for details

pages_404 = [109810, 1010136, 1011007, 1011358, 1011681, 1011848, 1012126, 
             1012294, 1012530, 1012692, 1012991, 1013220, 1013432, 1013490, 
             1013520, 1013576, 1013695, 1013698, 1013819, 1014484, 1014556, 
             1014606, 1014964, 1015588, 1015664, 1015669, 1015676, 1016128, 
             1016267, 1016492, 1016854, 1017051, 1017067, 1017564, 1018536]

df_imputed = df_imputed[~df_imputed.page_id.isin(pages_404)]

### Rearranging the columns in a nice order ###

df_imputed = df_imputed[['old_index', 'page_id', 'date', 
       'url', 'publish_date', 'word_count', 
       'classification_product', 'classification_type', 
       'page_name', 'authors', 'title', 
       'daily_likes', 'daily_dislikes', 
       'video_play', 'page_impressions',
       'clickouts', 'external_clicks', 'external_impressions']]

df_imputed.to_csv('data/merged_data.csv', encoding='utf-8', index=False)

print('The full dataframe is saved as data/merged_data.csv')

print('======== Processing complete ========')
