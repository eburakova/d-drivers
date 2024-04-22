import pandas as pd

# Read file:
print('======== This script engineers relevant features and merges scraped and provided data ========')

print('Reading the file...')

df_perf = pd.read_csv('data/data_aggr_page_id.csv', parse_dates=['date_max', 'date_min'])
df_scrape = pd.read_csv('data/data_scraped.csv')
df_clickbait = pd.read_csv('data/clickbait.csv')
df_trend_match = pd.read_csv('data/data_trends_classified.csv')
df_video_widget = pd.read_csv('data/video_player_types_per_article.csv')

print('Reading complete. \nCreating the features...')

### Feature Engineering ###

## Target Variable ##

# Calculate the Click through rate based on external clicks and impressions
df_perf['ctr'] = df_perf['external_clicks'] / df_perf['external_impressions'] *100

## Features ##

# Function to extract last part of URL and clean it
def extract_last_part(url):
    url_text = url.rsplit('/', 1)[-1]
    cleaned_url = url_text.split('_')[0]
    cleaned_url_list = cleaned_url.split('-')
    return cleaned_url_list

# Apply the function to create a new column
df_scrape['url_text'] = df_scrape['url'].apply(extract_last_part)

# Sum up all list items per ongoing Version ID and merge with original df
df_feat = pd.merge(df_scrape, df_scrape.groupby('page_id')['url_text'].apply(lambda x: list(set(sum(x, [])))).reset_index(name='merged_url'), on='page_id', how='left')

# Transform media column
def media_type(df, media_type):
    if 'img-wrapper' in media_type or any(item in media_type for item in ['image-gallery', 'mb-lg-7', 'mb-8']):
        return 'img'
    elif any(item in media_type for item in ['mb-3', 'video-player', 'recobar']):
        return 'video'
    else:
        return 'other'

df_feat['media_type'] = df_scrape['media_type'].apply(lambda x: media_type(df_feat, x))

# Title length
df_feat['meta_title_len'] = df_feat['meta_title'].str.len()

# Meta description length
df_feat['meta_desc_len'] = df_feat['meta_description'].str.len()

# H1 length
df_feat['h1_len'] = df_feat['h1'].str.len()

# Abstract length
df_feat['abstract_len'] = df_feat['abstract'].str.len()

# URL length
df_feat['merged_url_len'] = df_feat['merged_url'].str.len()

# Does the title structure "[Intrigue]: [Our take on it]" makes it more clickbait-y?
df_feat['title_has_colon'] = df_feat['h1'].str.contains(':')

# How often did they tweak the article?
df_perf['mean_version_lifetime'] = (df_perf['date_max'] - df_perf['date_min']).dt.days / (df_perf.no_versions + 1) 
# this is almost the inverse
df_perf['publ_freq'] = (df_perf.no_versions + 1) / ((df_perf['date_max'] - df_perf['date_min']).dt.days + 0.1)

# Targets normalized by n_days:
df_perf['ext_impr_norm'] = df_perf.external_impressions / df_perf.n_days

# number of urls (n_urls by n_ndays an n_urls by age) normalized
df_perf['urls_per_age'] = df_perf.n_urls / df_perf.age
df_perf['urls_per_days'] = df_perf.n_urls / df_perf.n_days

### Merging ###

# Define the merge keys
merge_keys = ['page_id']

# Perform the first merge
df_full = pd.merge(left=df_perf, right=df_feat, how='left', on=merge_keys)

df_clickbait['clickbait_prob'] = df_clickbait['score']

df_clickbait.loc[df_clickbait.label == "Not Clickbait", 'clickbait_prob'] *= -1
# Perform the second merge with df_clickbait
df_full = pd.merge(left=df_full, right=df_clickbait[['clickbait_prob', 'label', 'score', 'page_id']], how='left', on=merge_keys)

# Perform the third merge with df_trend_match
df_full = pd.merge(left=df_full, right=df_trend_match[['predicted_probability', 'predicted_query_label','query_score', 'page_id']], how='left', on=merge_keys)

# Perform the third merge with video widget feature
df_full = pd.merge(left=df_full, right=df_video_widget[['video_player_types', 'page_id']], how='left', on=merge_keys)

df_full.drop(['url_text','url_y'],axis=1,inplace=True)

df_full.rename(columns={'url_x':'url',
                        'author':'scraped_author',
                        'main_text_length':'scraped_word_count',
                        'label': 'clickbait_label', 
                        'score': 'clickbait_prob_raw',
                        'predicted_probability': 'google_trend_prob',
                        'predicted_query_label': 'google_trend_label',
                        'query_score': 'google_trend_score'
                        }, inplace=True)

### Writing to the file ###
print('Writing the final data frame to file...')
df_full.to_csv('data/data_features.csv', encoding='utf-8', index=False)
print('The full dataframe with features is saved as data/data_features.csv')

print('======== Processing complete ========')