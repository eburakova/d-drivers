from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
import pandas as pd
import streamlit as st
# import altair as alt

from functions import plot_feature_distribution, plot_feature_influence

# Set page title and favicon
st.set_page_config(
    page_title="Data Overview",
    page_icon="🟦",
    layout="wide",
)
 
# Load DataFrame
df = pd.read_csv('../data/preprocessing_nlp_v4.csv')

# Page title and image
st.image("DATA-DRIVEN SEARCH FOR TRAFFIC DRIVERS.png", use_column_width=True)
st.title("Composition of dataset")

# Sidebar menu
feature = st.selectbox('Select Feature:', ['word_count', 'classification_product', 'classification_type',
                                            'meta_title_len', 'meta_desc_len', 'h1_len', 'abstract_len',
                                            'sentiment_abstract_neutral', 'sentiment_abstract_positive',
                                            'video_standard_and_widget', 'video_widget', 'not_clickbait',
                                            'title_has_colon_True', 'media_type_video', 'Authors'],
                                            index=1)

option = st.selectbox('Select metric', ['Feed impressions', 'Click-through'])
if option == "Feed impressions":
    metric_name = 'external_impressions'
elif option == "Click-through":
    metric_name = 'ctr'
# Filter dataframe based on selected feature
df_filtered = df[[feature]]

# Calculate frequency of each category
freq_df = df_filtered[feature].value_counts().reset_index()
freq_df.columns = [feature, 'count']

# # Create bar chart for count
# bar_count = alt.Chart(freq_df).mark_bar().encode(
#     x=alt.X(f"{feature}:N", title=feature.capitalize()),
#     y=alt.Y('count:Q', title='Count'),
#     tooltip=['count:Q']
# ).properties(
#     width=600,
#     height=400
# ).configure_axis(
#     labelFontSize=12,
#     titleFontSize=14
# ).configure_title(
#     fontSize=16
# )

# # Filter dataframe based on selected option
# df_filtered_option = df[[feature, metric_name]]

# # Create bar chart for performance
# bar_performance = alt.Chart(df_filtered_option).mark_bar().encode(
#     x=alt.X(f"{feature}:N", title=feature.capitalize()),
#     y=alt.Y(f"{metric_name}:Q", title=metric_name.capitalize())
# ).properties(
#     width=600,
#     height=400
# ).configure_axis(
#     labelFontSize=12,
#     titleFontSize=14
# ).configure_title(
#     fontSize=16
# )

# Display the charts side by side
col1, col2 = st.columns([2, 2])
with col1:
    st.markdown(f"### Distribution of features", unsafe_allow_html=True)
    #st.write(bar_count)
    fig1 = plot_feature_distribution(feature, df)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown(f"### Influence on the metric", unsafe_allow_html=True)
    fig2 = plot_feature_influence(feature, metric_name, df)
    st.plotly_chart(fig2, use_container_width=True)
    #st.write(bar_performance)
