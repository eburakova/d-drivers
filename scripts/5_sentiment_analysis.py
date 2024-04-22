import os
import warnings
import pandas as pd
from transformers import pipeline
from tqdm import tqdm

# NOTE THAT AT THE END I INTRODUCE ONE MORE COLUMN 'df_full.sentiment_title'. CHANGE THE LAST LINE FOR 'abstract' OPTION.

df = pd.read_csv('data/data_features.csv')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # supressing warnings
warnings.filterwarnings("ignore")  

print(' ...maybe would be good idea to go for a walk, or contemplate nature. This code will take more than 5 minutes')

model_name = "oliverguhr/german-sentiment-bert"# initialize sentiment analysis pipeline
nlp = pipeline("sentiment-analysis", model=model_name)

# # a function for sentiment analysis
def get_sentiment(text):
    text = str(text)
    if text and text != 'nan': # in case the text is empty
        result = nlp(text)
        label = result[0]['label']
        score = result[0]['score']
        return label, score
    else:
        return 'neutral', None

# apply. Change here to make a sentiment analysis over 'abstract' or whatever else in a new column 
tqdm.pandas(desc="Sentiment Analysis of Abstract")
df[['sentiment_abstract', 'confidence_abstract']] = df['abstract'].progress_apply(lambda x: pd.Series(get_sentiment(x)) if pd.notnull(x) else pd.Series(['neutral', None]))
tqdm.pandas(desc="Sentiment Analysis of Meta Title")
df[['sentiment_meta_title', 'confidence_meta_title']] = df['meta_title'].progress_apply(lambda x: pd.Series(get_sentiment(x)) if pd.notnull(x) else pd.Series(['neutral', None]))

print('Writing the final data frame to file...')
df.to_csv('data/data_nlp.csv', encoding='utf-8', index=False)
print('The full dataframe with features is saved as data/data_nlp.csv')

print('======== Processing complete ========')