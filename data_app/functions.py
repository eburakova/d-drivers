import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pytrends.request import TrendReq

def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

def top_N_now(N, selected_metric="Feed impressions", df_dynamics=None):
    """
    Which articles are having a blast on the feed right now?

    Note: I thought of implementing the top gainers and loosers approach
    but the percent change upon republish is way too high! It is inconvenient
    
    BTW, this returns the last readings only, even if they were 
    months ago. Won't fix for the graduation
    
    Parameters:
    - N: return N performers
    - selected_metric: feed impressions or the clickthrough
    - df_dynamics: the dynamics.csv or any variation of this
    
    """
    # Team's convenience aka back-compatibility:
    if selected_metric=="external_impressions":
        selected_metric = "Feed impressions"
    
    if selected_metric.lower()=='ctr':
        selected_metric = "Click-through"
        
    if df_dynamics is None:
        df_dynamics = pd.read_csv('../data/dynamics.csv')
    hot = df_dynamics[['ID', 'Date', selected_metric]]\
                    .groupby('ID', as_index=False).agg('last')
    return hot.sort_values(selected_metric).tail(N)

def top_N_clicked(N, df=None):
    """
    Which articles are most clicked on? 
    """
    if df is None:
        df = pd.read_csv('../data/data_nlp_A.csv')
    pass

def topics_heatmap(df=None, metric_name="Feed impressions"):
    if df is None:
        df = pd.read_csv('../data/data_nlp_A.csv')
    metric_name = metric_name.lower()

    # Preparing thte data
    pivot = pd.pivot_table(data=df,
        index='classification_type', 
        columns='classification_product',
        values='external_impressions',
        aggfunc='median')
    pivot = pivot.sort_index(axis=0)
    pivot = pivot.sort_index(axis=1)
    n_x_ticks = len(pivot.columns)
    n_y_ticks = len(pivot.index)
    heatmap = go.Heatmap(
            z=pivot.values,
            colorscale='Blues',  # Gradient colormap from light to deep blue
            hoverongaps=False,  # Do not show hover info on gaps
            hovertemplate='Median ' + metric_name + ': %{z}<br>X: %{x}<br>Y: %{y}',  # Custom tooltip with bin height and coordinates
            colorbar=None
        )

    # Customize layout
    y_tick_positions = [t+0.0 for t in range(n_y_ticks)]
    y_tick_positions.reverse()
    y_tick_labels = list(pivot.index)
    y_tick_labels.reverse()

    layout = go.Layout(
        template='simple_white',
        width=500,
        height=500,
        xaxis=dict(tickmode='array', 
                tickvals=[t+0.0 for t in range(n_x_ticks)], 
                ticktext=pivot.columns,
                tickangle=60),  # Horizontal axis labels
        yaxis=dict(tickmode='array', 
                tickvals=y_tick_positions, 
                ticktext=y_tick_labels),  # Vert axis labels
        margin=dict(l=30, r=30, t=30, b=30),  # Adjust margins
    )

    # Create figure
    fig = go.Figure(data=[heatmap], 
                    layout=layout,
                    )

    # Show plot
    return fig

def plot_metric_history(selected_metric, df_dynamics=None):
    if df_dynamics is None:
        df_dynamics = pd.read_csv('../data/dynamics.csv')
    if selected_metric == "Feed impressions":
        data = df_dynamics[['Date', selected_metric]].groupby('Date').sum()
    else: 
        data = df_dynamics[['Date', selected_metric]].groupby('Date').median()
    fig_bar = px.bar(data, color_discrete_sequence=['#252f91'])
    
    layout = go.Layout(
        template='simple_white',
        #width=500,
        height=300,
        xaxis=dict(),  # Horizontal axis labels
        yaxis=dict(title=selected_metric,
                   tickmode='array', 
                tickvals=[1e6], 
                ticktext=['[Concealed]']),  # Vert axis labels
        margin=dict(l=30, r=30, t=30, b=30),  # Adjust margins
    )

    fig_bar.update_layout(layout)
    return fig_bar


def plot_feature_distribution(feature, df=None, feature_name=None):
    if df is None:
        df = pd.read_csv('./data/preprocessing_nlp_v4.csv')
    if feature_name is None:
        feature_name = feature

    fig = px.histogram(df, x=feature, color_discrete_sequence=['#252f91'])
    layout = go.Layout(
        template='simple_white',
        #width=500,
        height=500,
        xaxis=dict(title=feature_name, tickangle=60),  # Horizontal axis labels
        yaxis=dict(title='Count',
                   tickmode='array'),  # Vert axis labels
        margin=dict(l=30, r=30, t=30, b=30),  # Adjust margins
    )

    fig.update_layout(layout)
    return fig

def plot_feature_influence(feature, metric, df=None, 
                           feature_name=None, 
                           metric_name=None):
    if df is None:
        df = pd.read_csv('./data/preprocessing_nlp_v4.csv')
    if feature_name is None:
        feature_name = feature
    if metric_name is None:
        metric_name = metric

    fig_sc = px.scatter(df, x=feature, y=metric, 
                        marginal_x="rug", marginal_y="rug",
                        color_discrete_sequence=['#252f91'])
    layout = go.Layout(
        template='simple_white',
        #width=500,
        height=500,
        xaxis=dict(title=feature_name, tickangle=60),  # Horizontal axis labels
        yaxis=dict(title=metric_name),   # Vert axis labels
        margin=dict(l=30, r=30, t=30, b=30),  # Adjust margins
    )

    fig_sc.update_layout(layout)
    return fig_sc

from transformers import pipeline

model_name = "./sentiment/"# initialize sentiment analysis pipeline
sent_model = pipeline("sentiment-analysis", model=model_name)
def get_sentiment(text="Ich fahre mein E-Bike sehr gerne!"):
    text = str(text)
    if text and text != 'nan': # in case the text is empty
        result = sent_model(text)
        label = result[0]['label']
        score = result[0]['score']
        return label.capitalize(), round(score*100, 2)
    else:
        return 'Neutral', None

def request_interest_over_time(term, timeframe):
    pytrends = TrendReq(hl='de-DE', tz=360)
    pytrends.build_payload(kw_list=[term],
                       cat=0, # Category:0 for all categories (see https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories for all)
                       timeframe=timeframe,
                       geo='DE', # Geographic location, in this case 'Deutschland'
                       gprop='') # Google Search Property, e.g. 'images' Defaults to web searches
    return pytrends.interest_over_time()

import time
def request_trends_individual(terms, timeframe='2023-01-01 2024-03-23'):
    interest_df = request_interest_over_time(terms[0], timeframe)
    interest_df = interest_df.drop('isPartial', axis=1)
    if len(terms) > 1:
        for term in terms[1:]:
            interest_df_term = request_interest_over_time(term, timeframe)
            interest_df_term = interest_df_term.drop('isPartial', axis=1)
            interest_df = interest_df.join(interest_df_term) 
            time.sleep(.5)
    return interest_df

def plot_interest(interest_over_time_df):
    fig = px.line(interest_over_time_df, 
        color_discrete_sequence=[
            '#252f91', '#ff9800', '#a52670', '#0c600f', '#1a98ce', '#7026a5', '#000000','#9fa526'
            ]
                 )