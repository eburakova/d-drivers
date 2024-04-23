import warnings
import os
#from transformers import pipeline
import streamlit as st
import streamlit_shadcn_ui as ui

from functions import get_sentiment

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Sentiment analysis",
    page_icon='🎭'
    #layout="wide"
)
# Page title and image
st.image("DATA-DRIVEN SEARCH FOR TRAFFIC DRIVERS.png", use_column_width=True)
st.title("Sentiment checker")

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # supressing warnings
warnings.filterwarnings("ignore")  

# model_name = "./sentiment/"# initialize sentiment analysis pipeline
# nlp = pipeline("sentiment-analysis", model=model_name)

cols_top = st.columns([0.5, 0.5])
with cols_top[0]:
    st.markdown("""How would your text feel to the readers? 
                
Check the sentiment here.""")
with cols_top[1]:
    st.info(icon="💡", body="""Model: \n
[German Sentiment BERT by Oliver Guhr](https://huggingface.co/oliverguhr/german-sentiment-bert)""")
# def get_sentiment(text):
#     text = str(text)
#     if text and text != 'nan': # in case the text is empty
#         result = nlp(text)
#         label = result[0]['label']
#         score = result[0]['score']
#         return label.capitalize(), round(score*100, 2)
#     else:
#         return 'Neutral', None

text = ui.textarea(default_value="Ich fahre mein E-Bike sehr gerne!", placeholder="Enter your text", key="textarea1")

### text = st.text_input('Paste your text here', 'Ich fahre mein E-Bike sehr gerne!')
text = text.lower()
label, score = get_sentiment(text)

with ui.card(key="card1"):
    #ui.element("span", children=["Result"], className="text-gray-400 text-sm font-medium m-1", key="label1")
    if label == 'Positive':
        ui.element("span", children=[f"{label}"], className="text-green-400 text-sm font-medium m-1", key="label2")
        ui.element("span", children=[f"Confidence score {score} %"], className="text-gray-400 text-sm font-medium m-1", key="label3")
        #st.markdown(f"**:green[{label}]**")
    elif label == 'Negative':
        ui.element("span", children=[label], className="text-red-400 text-sm font-medium m-1", key="label2")
        ui.element("span", children=[f"Confidence score {score} %"], className="text-gray-400 text-sm font-medium m-1", key="label3")
        #st.markdown(f"**:red[{label}]**")
    else:
        if text:
            ui.element("span", children=[label], className="text-blue-400 text-sm font-medium m-1", key="label2")
            ui.element("span", children=[f"Confidence score {score} %"], className="text-gray-400 text-sm font-medium m-1", key="label3")

        #st.markdown(f"**:blue[{label}]**")
    #ui.element("span")
    #ui.element()
    #ui.element("span", children=[f"Confidence score {round(score*100, 2)} %"], className="text-gray-400 text-sm font-medium m-1", key="label3")
    # st.caption(f"""Confidence: {round(score*100, 2)} %""")



# with col[1]:
    #st.markdown(label)
#st.caption(f"""Confidence: {round(score*100, 2)} %""")
