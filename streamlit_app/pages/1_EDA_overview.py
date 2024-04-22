from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
import pandas as pd
import streamlit as st
 
# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Data overview",
    layout="wide"
)
 
# Establish communication between pygwalker and streamlit
init_streamlit_comm()
 
# Add a title
st.title("General overview of the data")
 
# Get an instance of pygwalker's renderer. You should cache this instance to effectively prevent the growth of in-process memory.
@st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    df = pd.read_csv('../data/sl_app/eda_total.csv')
    # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
    return StreamlitRenderer(df, spec="./pages/pyg_specs/summary.json", debug=False, show_cloud_tool=False)
 
renderer = get_pyg_renderer()
 
# Render your data exploration interface. Developers can use it to build charts by drag and drop.
renderer.render_explore()
 