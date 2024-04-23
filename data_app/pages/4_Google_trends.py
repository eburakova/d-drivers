import streamlit as st
import plotly.express as px
 
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

from pytrends.request import TrendReq
pytrends = TrendReq(hl='de-DE', tz=360, timeout=(10,25),  retries=2, backoff_factor=0.1)

start = st.date_input("Select the start date")
end = st.date_input("Select the end date", "today")

# st.write(start)
# st.write(end)

term = st.text_input(label="Enter the term", value="E-Auto")
#timeframe = '2023-01-01 2024-03-23'  # custom date range works but the retured values are binned week-wise
timeframe = f'{start} {end}'

@st.cache_resource
def request_interest_over_time(term, timeframe):
    pytrends = TrendReq(hl='de-DE', tz=360)
    pytrends.build_payload(kw_list=[term],
                       cat=0, # Category:0 for all categories (see https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories for all)
                       timeframe=timeframe,
                       geo='DE', # Geographic location, in this case 'Deutschland'
                       gprop='') # Google Search Property, e.g. 'images' Defaults to web searches
    return pytrends.interest_over_time()
    
if st.button('Search'):
    interest_over_time_df = request_interest_over_time(term, timeframe)

    cols = st.columns(2)
    with cols[0]:
        st.dataframe(interest_over_time_df)
    with cols[1]:
        trend_fig = px.line(x=interest_over_time_df.index, y=interest_over_time_df[term],
                            color_discrete_sequence=['#252f91'])
        st.plotly_chart(trend_fig, use_container_width=True)


