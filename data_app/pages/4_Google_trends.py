import streamlit as st
import plotly.express as px
import pandas as pd
from pytrends.request import TrendReq

from functions import request_interest_over_time, request_trends_individual

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Google trends",
    page_icon='📈',
    layout="wide"
)
st.image("DATA-DRIVEN SEARCH FOR TRAFFIC DRIVERS.png", use_column_width=True)
st.title("Explore Google trends")
st.header("Interest over time")
st.info("""
Numbers represent search interest relative to the highest point on the chart for the given region and time. 
* A value of 100 is the peak popularity for the term. 
* A value of 50 means that the term is half as popular. 
* A score of 0 means there was not enough data for this term.
""")

pytrends = TrendReq(hl='de-DE', tz=360, timeout=(10,25),  retries=2, backoff_factor=0.1)

start = st.date_input("Select the start date")
end = st.date_input("Select the end date", "today")

# st.write(start)
# st.write(end)

term_in = st.text_input(label="Enter the terms (separate by comma)", value="E-Auto, Auto kaufen")
#timeframe = '2023-01-01 2024-03-23'  # custom date range works but the retured values are binned week-wise
timeframe = f'{start} {end}'

terms = term_in.split(',')
#terms = [f'({t})' for t in terms]

#@st.cache_resource
#st.checkbox('Individual', )
if st.button('Check'):

    interest_over_time_df = request_trends_individual(terms)

    cols = st.columns([0.3, 0.7])
    with cols[0]:
        st.dataframe(interest_over_time_df)
    with cols[1]:
        trend_fig = px.line(interest_over_time_df, 
                            #template='simple_white',
                            color_discrete_sequence=[
                                '#252f91', '#ff9800', '#a52670', '#0c600f', '#1a98ce', '#7026a5', '#000000','#9fa526'
                                ]
                            )
        st.plotly_chart(trend_fig, use_container_width=True)

    st.download_button(label="Download the trend data as csv", 
                   data=interest_over_time_df.to_csv(),
                   file_name="trends.csv",
                   mime='text/csv')
