import streamlit as st
from typing import Dict
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from sklearn.preprocessing import PowerTransformer
import pickle
from typing import Dict, List

# Set page title and favicon
st.set_page_config(
    page_title="Prediction - Article Impressions",
    page_icon="🟦",
    layout="wide",
)

# Initialize PowerTransformer
file_path_specific = './pages/power_transformer_ext_impr.pkl'
with open(file_path_specific, 'rb') as file:
    loaded_pt = pickle.load(file)

def reverse_power_transformation(predicted_value, pt):
    if isinstance(predicted_value, float):
        # Reshape the predicted value for inverse transformation
        predicted_value_transformed = [[predicted_value]]
    else:
        # Reshape the predicted value for inverse transformation
        predicted_value_transformed = predicted_value.reshape(-1, 1)
    
    # Inverse transform the predicted value
    return loaded_pt.inverse_transform(predicted_value_transformed)


def predict_tabular_regression_sample(
    project: str,
    endpoint_id: str,
    instance_dict: Dict,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
) -> List[Dict]:
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    
    # Initialize client that will be used to create and send requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    
    # Parse the instance dictionary
    instance = json_format.ParseDict(instance_dict, Value())
    instances = [instance]
    
    # Prepare empty parameters
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    
    # Construct the endpoint path
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    
    try:
        # Send the prediction request
        response = client.predict(
            endpoint=endpoint, instances=instances, parameters=parameters
        )
        
        # Extract and return predictions
        return response.predictions
            
    except Exception as e:
        st.write(f"Error during prediction: {e}")
        st.write(f"Error type: {type(e)}")
        return []
    

#### Streamlit app ####

st.image("DATA-DRIVEN SEARCH FOR TRAFFIC DRIVERS.png", use_column_width=True)
st.title("Prediciton of Article Impressions")

# Text areas for Title, Abstract, and Article
title_text = st.text_input("Title", "Your Title Here")
abstract_text = st.text_area("Abstract", "Your Abstract Here")
article_text = st.text_area("Article", "Your Article Here")

# Input features
classification_product = st.selectbox("Classification Product", ['E-Auto', 'Auto', 'Zubehör', 'Motorrad', 'Energie', 'Verkehr','Wallbox/Laden', 'Solaranlagen', 'E-Bike', 'Fahrrad', 'E-Scooter','Solarspeicher', 'Balkonkraftwerk', 'Solargenerator', 'THG','Wärmepumpe', 'Versicherung'])
classification_type = st.selectbox("Classification Type", ['Ratgeber', 'News', 'Kaufberatung', 'Deal', 'Test','Erfahrungsbericht', 'Video'])
urls_per_days = st.slider("Publishing Frequency",min_value=0.0,max_value=0.5,step=0.01)
#video_standard_and_widget = st.selectbox("Video Standard and Widget", ["True", "False"])
media_type = st.radio("Media Type", ["Image","Video"])
if media_type == 'Video':
    video_widget = st.radio("Video type", ["Self-produced", "Generic video playlist"])
else:
    video_widget = 'False'
#n_days = st.slider("Expected time the article is online",0,20)
n_days = 15 # mean of n_days

# Count characters in Title, Abstract, and Article
h1_len = len(title_text)
meta_title_len = len(title_text)
abstract_len = len(abstract_text) 
meta_desc_len = abstract_len - 100
word_count = abstract_len+ len(article_text)

# Prepare instance dictionary
instance_dict = {
    "word_count": str(word_count),
    "classification_product": str(classification_product),
    "classification_type": str(classification_type),
    "urls_per_days": str(urls_per_days),
    "meta_title_len": str(meta_title_len),
    "meta_desc_len": str(meta_desc_len),
    "h1_len": str(h1_len),
    "abstract_len": str(abstract_len),
    "google_trend_label": str('elektroauto'),
    "google_trend_score": str(31.0),
    "video_standard_and_widget": str('False') if video_widget == 'True' else str('True'),
    "video_widget": str('True') if video_widget == 'Self-produced' else str('False'),
    "media_type_other": str('False'),
    "media_type_video": str('True') if media_type == 'Video' else str('False'),
    "Authors": str("lemur")
}

# Button to trigger prediction
if st.button("Predict"):
    predictions = predict_tabular_regression_sample(
        project="101568381799",
        endpoint_id="5222247024354656256",
        instance_dict=instance_dict,
        location="us-central1",
        api_endpoint="us-central1-aiplatform.googleapis.com"
    )

    if predictions:
        prediction_value = predictions[0].get('value', None)
        lower_bound = predictions[0].get('lower_bound', None)
        upper_bound = predictions[0].get('upper_bound', None)
        
        if prediction_value is not None and lower_bound is not None and upper_bound is not None:
            reversed_value = (reverse_power_transformation(prediction_value, loaded_pt))*n_days
            reversed_lower_bound = (reverse_power_transformation(lower_bound,loaded_pt)) *n_days
            reversed_upper_bound = (reverse_power_transformation(upper_bound,loaded_pt)) *n_days
            
            # Format numbers without commas and decimals
            formatted_reversed_value = "{:,.0f}".format(reversed_value[0][0]).replace(',', '')
            formatted_lower_bound = "{:,.0f}".format(reversed_lower_bound.item()).replace(',', '')
            formatted_upper_bound = "{:,.0f}".format(reversed_upper_bound.item()).replace(',', '')
            
            st.markdown(f"<h2>Predicted Impressions: {formatted_reversed_value}</h2>", unsafe_allow_html=True)
            st.write(f"Lower Bound: {formatted_lower_bound}")
            st.write(f"Upper Bound: {formatted_upper_bound}")
            
        else:
            st.write("Incomplete prediction data received.")
        
    else:
        st.write("No valid predictions received.")
