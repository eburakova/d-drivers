######################################################
#                     OUTDATED                       #
#        Please use merge_source.py instead          #
######################################################

## For explanations see ./notebooks/Cleaning-categorising-katja.ipynb

import pandas as pd
### from timeit import timeit

# Read part of the malformatted file:
print('======== This is the script that combines and tidies up the raw data ========')
print('The run should take approx. 30 seconds.')
print()
print('Reading the first file...')

df1 = pd.read_excel('data/data_d-drivers_2024-03-24.xlsx', sheet_name='data',
                    usecols=['PAGE_EFAHRER_ID', 'DATE', 'PAGE_CANONICAL_URL', 'PAGE_AUTHOR', 'WORD_COUNT', 'CLICKOUTS']
                    )
print('Reading the second file...')
#Read everything from the new file:
df2 = pd.read_excel('data/data_d-drivers_2024-03-26.xlsx', sheet_name='data')

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

### Version count ###
print('''Calculating version IDs...
     ->  Hint: version changes when any of the folowing change: word count, publish_date or the authors''')

temp = df_imputed[['page_id', 'word_count', 'publish_date', 'authors']].drop_duplicates().copy()
#temp = temp.fillna({'word_count': 0, 'publish_date': pd.Timestamp('2018-01-01 00:00')})
temp = temp.drop_duplicates()
temp = temp.sort_values('publish_date')

wc_versions = temp.groupby('page_id')['word_count'].transform(lambda x: pd.factorize(x)[0])
publish_versions = temp.groupby('page_id')['publish_date'].transform(lambda x: pd.factorize(x)[0])
authors_versions = temp.groupby('page_id')['authors'].transform(lambda x: pd.factorize(x)[0])

version_count = 10000*wc_versions + 1000*publish_versions + 1*authors_versions
temp['ver_id_wc'] = wc_versions
temp['ver_id_pub'] = publish_versions
temp['ver_id_auth'] = authors_versions
temp['version_id_raw'] = version_count
temp['version_id'] = temp.groupby('page_id')['version_id_raw'].transform(lambda x: pd.factorize(x)[0])

df_versions = pd.merge(left=df_imputed, right=temp.drop(['ver_id_wc', 'ver_id_pub', 'ver_id_auth', 'version_id_raw'], axis=1),
         on=['page_id', 'word_count', 'publish_date', 'authors'],
         how='left')

### Including the scraped data ###
# THANKS @CLARA 
print('Merging with the scraped data...')

df_scraped = pd.read_csv('data/scraping_no_duplicates.csv')
df_scraped.columns = [col.lower() for col in df_scraped.columns]

df_scraped.rename({
           #'impressions': 'page_impressions',
           'words': 'words_scraped',
           'page_efahrer_id': 'page_id',
           'page_canonical_url': 'url',
           'author': 'author_scraped',
           'current_title': 'h1'
            }, axis=1, inplace=True)

merge_keys = ['page_id', 'url']
df_full = pd.merge(left=df_versions, right=df_scraped, on=merge_keys, how='left')
# May drop some columns
#df_full = df_full.drop(['old_index'], axis=1)

### Final touch
df_full = df_full[['old_index', 'page_id', 'date', 'url', 'version_id', 'publish_date',
       'word_count', 'words_scraped', 'classification_product', 'classification_type', 
       'page_name', 'authors', 'author_scraped',
       'title', 'h1', 'abstract', 'last_update', 'image_url',
       'daily_likes', 'daily_dislikes', 'video_play', 'page_impressions',
       'clickouts', 'external_clicks', 'external_impressions']]

### Writing to the file ###
print('Writing the final data frame to file...')
df_full.to_csv('./data/full_data.csv', encoding='utf-8', index=False)
print('The full dataframe is saved as ./data/full_data.csv')

print('======== Processing complete ========')
