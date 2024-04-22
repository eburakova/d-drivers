import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_option('deprecation.showPyplotGlobalUse', False)
# Function to perform basic EDA
def perform_eda(df):
    # Display the first few rows of the DataFrame
    st.subheader('First few rows of the DataFrame')
    st.write(df.head())

    # Display summary statistics
    st.subheader('Summary Statistics')
    st.write(df.describe())

    # Display correlation heatmap
    st.subheader('Correlation Heatmap')
    fig = plt.figure(figsize=(12, 10))
    cmatr = df.select_dtypes(include=['int', 'float']).corr()
    THRESH = st.slider('Correlation threshold', 0.0, 0.9, 0.5)
    mask = np.abs(cmatr) > THRESH
    sns.heatmap(cmatr, annot=True, cmap='coolwarm', fmt='.2f', ax=plt.gca(), mask=-mask)
    plt.tight_layout()
    st.pyplot(fig)

# Main function to run the Streamlit app
def main():
    # Set title and headline picture
    st.title('D-driver - Data-driven search for traffic drivers')
    st.image('title-d-driver.jpg', use_column_width=True)  # Add your headline picture

    # Add styled text
    st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="big-font">Upload a CSV file to perform basic EDA on your data.</p>', unsafe_allow_html=True)

    # Upload a CSV file
    uploaded_file = st.file_uploader('Upload a CSV file', type=['csv'])

    if uploaded_file is not None:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)

        # Check if the DataFrame is not empty
        if not df.empty:
            # Perform EDA
            perform_eda(df)
        else:
            st.write('DataFrame is empty.')

# Run the app
if __name__ == '__main__':
    main()
