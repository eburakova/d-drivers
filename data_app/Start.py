import streamlit as st
import streamlit_shadcn_ui as ui

import pandas as pd
from functions import *

# Set page title and favicon
st.set_page_config(
    page_title="Start - Data Overview",
    page_icon="🟦",
    layout="wide",
    menu_items={
         'Report a bug': "mailto:admin@d-drivers.com",
         'About': """# D-Drivers data app 
This is a demo data exploration tool for D-Drivers. Meant for internal use."""
        }
        )


# Load DataFrame
# TODO: optimize data load for god's sake!

df_static = pd.read_csv('data/data_nlp_A.csv')
df_dyn = pd.read_csv('data/dynamics.csv')

n_pages = df_static.page_id.unique().shape[0]

# Page title and image
st.image("DATA-DRIVEN SEARCH FOR TRAFFIC DRIVERS.png", use_column_width=True)
st.title("Content base overview")

selected_metric = st.selectbox(
    'Select metric',
    ('Feed impressions', 'Click-through')
    )
fig_bar = plot_metric_history(selected_metric, df_dyn)
fig_bar.update_traces(showlegend=False)
st.plotly_chart(
    fig_bar,
       use_container_width=True)

cols = st.columns(3)

total_impressions = df_static.external_impressions.sum()
median_ctr = round(df_dyn.ctr.median(), 1)

with cols[0]:
    ui.metric_card(title="Total articles", content=f"{n_pages}", description="", key="card1")
with cols[1]:
    ui.metric_card(title="Total feed impressions", content=format_number(total_impressions), description="", key="card2")
with cols[2]:
    ui.metric_card(title="Median click-trough rate", content=f"{median_ctr} %", description="", key="card3")

cols2 = st.columns([0.3, 0.7])
with cols2[0]:
    
    top_page = top_N_now(1, selected_metric, df_dyn)
    its_id = top_page.iloc[-1, 0]
    its_title = df_static.query('page_id == @its_id').iloc[0,:].title.strip()
    if selected_metric == 'Feed impressions':
        description = format_number(top_page.iloc[-1, -1]) + ' ' + selected_metric.lower()
    elif selected_metric == 'Click-through':
        description = str(top_page.iloc[-1, -1].round(2)) + '% ' + selected_metric.lower()
    ui.metric_card(title="Top trending", content=its_title, description=description, key="card4")

with cols2[1]:
    fig = topics_heatmap(df_static)
    st.plotly_chart(fig, use_container_width=True)