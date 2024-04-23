from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
import pandas as pd
import streamlit as st
 
# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Interactive exploration",
    layout="wide",
    page_icon='📊',
)
 
# Establish communication between pygwalker and streamlit
init_streamlit_comm()
 
# Get an instance of pygwalker's renderer. You should cache this instance to effectively prevent the growth of in-process memory.
@st.cache_resource
def get_pyg_renderer(data_path, spec_path) -> "StreamlitRenderer":
    df = pd.read_csv(data_path)
    # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
    return StreamlitRenderer(df, spec=spec_path, 
                             show_cloud_tool=False,
                             theme_key='g2',
                             spec_io_mode='rw',
                             appearance='light',
                             )

# Add a title
st.title("General overview of the data")

mode = st.selectbox('Select exploration mode',
    ('Overview', 'Details', 'Page by page dynamics', 'Freestyle'))

if mode == 'Overview':
    data_path = './data/eda_total.csv'
    spec_path = "./pages/pyg_specs/summary.json"
elif mode == 'Details':
    data_path = './data/eda_scatters.csv'
    spec_path = "./pages/pyg_specs/eda_features_sl.json"
elif mode == 'Page by page dynamics':
    data_path = './data/dynamics.csv'
    spec_path = "./pages/pyg_specs/history.json"
else:
    data_path = './data/data_nlp_A.csv'
    spec_path = './pages/pyg_specs/empty.json'
 
renderer = get_pyg_renderer(data_path, spec_path)

# Render your data exploration interface. Developers can use it to build charts by drag and drop.
renderer.explorer()