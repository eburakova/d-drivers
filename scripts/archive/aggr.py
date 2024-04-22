import pandas as pd

df = pd.read_csv('data/full_data.csv')

df_aggr = df[['page_id', 'date', 'publish_date', 'word_count', 'authors']]
df_aggr.loc[:, 'authors'] = df_aggr.authors.apply(lambda s: s.replace(' und ', ';'))

df_aggr = df_aggr[['page_id', 'date', 'publish_date', 'word_count', 'authors']]\
    .groupby(['page_id', 'date', 'publish_date', 'word_count']) \
        .agg(lambda auth: ';'.join(auth))

df_aggr = df_aggr.authors.apply(lambda auths: sorted(list(set(auths.split(';'))))).to_frame()

df = pd.merge(df.drop(['authors'], axis=1), 
        df_aggr,
        on=['page_id', 'date', 'publish_date', 'word_count'], how='left')

df.loc[:, 'authors'] = df.loc[:, 'authors'].apply(lambda l: str(l))
df.loc[:, 'authors'] = df.authors.apply(''.join)

temp = df[['page_id', 'word_count', 'publish_date', 'authors']].copy()
temp.drop_duplicates(inplace=True)

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
temp['version_id_new'] = temp.groupby('page_id')['version_id_raw'].transform(lambda x: pd.factorize(x)[0])

df_versions = pd.merge(left=df, right=temp.drop(['ver_id_wc', 'ver_id_pub', 'ver_id_auth', 'version_id_raw'], axis=1),
         on=['page_id', 'word_count', 'publish_date', 'authors'],
         how='left')

df_versions.to_csv('data/aggr_data.csv', index=False)