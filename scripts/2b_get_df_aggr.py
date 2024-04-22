import pandas as pd

df = pd.read_csv('data/merged_data.csv', parse_dates=['date', 'publish_date'])

print('! The end dataframe should have this many rows:', df.drop_duplicates(['page_id', 'date']).shape[0])
print('-> The dataframe has this many rows:', df.shape[0])

# ------------------------------------------------------------ #
# Aggregating the different authors into a list of 
# all people who took part in writing and editing the article
# ------------------------------------------------------------ #

print('\n Aggregating authors...')

df_aggr_authors = df[['page_id', 'date', 'publish_date', 'word_count', 'authors']]
df_aggr_authors.loc[:, 'authors'] = df_aggr_authors.authors.str.replace(' und ', ';')
df_aggr_authors.loc[:, 'authors'] = df_aggr_authors.authors.str.replace(' & ', ';')
df_aggr_authors.loc[:, 'authors'] = df_aggr_authors.authors.str.replace(' / ', ';')


df_aggr_authors = df_aggr_authors[['page_id', 'date', 'publish_date', 'word_count', 'authors']]\
    .groupby(['page_id', 'date', 'publish_date', 'word_count']) \
        .agg(lambda auth: ';'.join(auth))

df_aggr_authors = df_aggr_authors.authors.apply(lambda auths: sorted(list(set(auths.split(';'))))).to_frame()

df = pd.merge(df.drop(['authors'], axis=1), 
        df_aggr_authors,
        on=['page_id', 'date', 'publish_date', 'word_count'], how='left')

print('-> The dataframe has this many rows:', df.shape[0])

df.loc[:, 'authors'] = df.authors.apply(lambda a: ';'.join(a))

# ------------------------------------------------------------ #
# Aggregating the urls into a universal list of 
# all URLs that have ever been crafted for this article  
# ------------------------------------------------------------ #
print('\n Aggregating urls...')

url_col = df[['page_id', 'date', 'url']]

url_col = url_col[['page_id', 'date', 'url']]\
    .groupby(['page_id', 'date']) \
        .agg(lambda url: ';'.join(url))

url_col = url_col.url.apply(lambda urls: sorted(list(set(urls.split(';')))))
url_col = url_col.apply(';'.join).to_frame().reset_index()

df = pd.merge(df.drop(['url'], axis=1), 
        url_col,
        on=['page_id', 'date'], how='left')

print('-> The dataframe has this many rows:', df.shape[0])

# ------------------------------------------------------------ #
# Aggregate all propertied that depdnd on the URLs. 
# Consider only the effect of the "major" URL -
# the one that acquired the most traffic!
# ------------------------------------------------------------ #

df_agg_url = df[['page_id', 'date', 'url', 'video_play', 'page_impressions', 'clickouts']]\
                .groupby(['page_id', 'date', 'url'])\
                .max()

# ------------------------------------------------------------ #
# Count the versions based on publish_date and word_count
# ------------------------------------------------------------ #

print('''
Calculating version IDs...
     ->  Hint: version changes when any of the folowing change: word count, publish_date or the authors''')

temp = df[['page_id', 'word_count', 'publish_date', 'authors']].drop_duplicates().copy()
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

df = pd.merge(left=df, right=temp.drop(['ver_id_wc', 'ver_id_pub', 'ver_id_auth', 'version_id_raw'], axis=1),
         on=['page_id', 'word_count', 'publish_date', 'authors'],
         how='left')

print('-> The dataframe has this many rows:', df.shape[0])

# Clean-up
del temp
del publish_versions
del authors_versions

print('\n Aggregating...')
# ------------------------------------------------------------ #
# Aggregate the properties that change with the publish date
# ------------------------------------------------------------ #

df_agg_page_date_pubdate =  df[['page_id', 'date', 'publish_date', 'daily_likes', 'daily_dislikes']]\
                .groupby(['page_id', 'date', 'publish_date'])\
                .sum()

# ------------------------------------------------------------ #
# Aggregate the properties that are constant for the given date
# ------------------------------------------------------------ #

df_agg_page_date = df.drop(['old_index', # don't really need it
                        'url', 'video_play', 
                        'page_impressions', 'clickouts', 
                        'daily_likes', 'daily_dislikes'], axis=1)\
                .groupby(['page_id', 'date'])\
                .agg(
                        {
                        'publish_date': 'max',
                        'word_count': 'last',
                        'classification_product': 'last',
                        'classification_type': 'last',
                        'page_name': 'last',
                        'version_id': 'max', # not always the same for the date but it should be
                        'title': 'last',
                        'authors': 'last', 
                        'external_clicks': 'sum', 
                        'external_impressions': 'sum'
                        }
                )

# Building the aggregated dataset
df_agg_full_0 = pd.merge(left=df[['page_id', 'date']].drop_duplicates(), 
                         right=url_col, on=['page_id', 'date'])
df_agg_full_1 = pd.merge(left=df_agg_full_0, right=df_agg_page_date, on=['page_id', 'date'], how='inner')
df_agg_full_2 = pd.merge(left=df_agg_full_1, right=df_agg_page_date_pubdate, on=['page_id', 'date'], how='inner')
df_agg_full_3 = pd.merge(left=df_agg_full_2, right=df_agg_url, on=['page_id', 'date', 'url'], how='inner')
df = df_agg_full_3.copy()

# # Clean-up
# del df_agg_full_0
# del df_agg_full_1
# del df_agg_full_2
# del df_agg_full_3
print('-> The dataframe has this shape:', df.shape)

# ------------------------------------------------------------ #
# Manual correction for the exception: duplicates on 
# - 10437 (29.10.23)
# - 101473 (11.11.23)
# - 1015387 (13.10.23)
# ------------------------------------------------------------ #

still_duplicated = ['word_count', 'daily_likes', 'daily_dislikes', 'video_play', 'page_impressions']
unique_cols = list(df.columns.drop(still_duplicated))

df = df.drop_duplicates(unique_cols)

diff = df[['page_id', 'date']].shape[0] - 107816
if diff == 0:
        print('The dataframe length is correct!')
else:
        print(f"Lengths don't match by {diff} rows :(")
print()

### Rearranging the columns in a nice order ###

df = df[['page_id', 'date', 'version_id', 'url', 'publish_date', 'word_count',
       'classification_product', 'classification_type', 'page_name',
        'title', 'authors', 'daily_likes', 'daily_dislikes', 'video_play',
        'page_impressions', 'clickouts', 
        'external_clicks', 'external_impressions']]

print('Writing to the file...')
df.to_csv('data/data_aggr.csv', index=False)

print('Aggregated data saved as "data/data_aggr.csv" ')
print()
print('======== Processing complete ========')
