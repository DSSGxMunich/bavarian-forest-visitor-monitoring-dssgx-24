# imports libraries
import streamlit as st
import altair as alt
from src.streamlit_app.pages_in_dashboard.data_accessibility.query_box import get_query_section
from src.streamlit_app.pages_in_dashboard.data_accessibility.upload import upload_section
from src.streamlit_app.pages_in_dashboard.data_accessibility.download import download_section

# Define the page layout of the Streamlit app

st.set_page_config(
page_title='Access the park data🌲',
page_icon="🌲",
layout="wide",
initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Define the app layout

col1, col2 = st.columns((1.5,2), gap='medium')
with col1:
    # get_upload_and_download_section()
    st.markdown("## Data Access Point")

    # Tabs for Upload and Download
    tab1, tab2 = st.tabs(["Upload Data", "Download Data"])
    if tab1:
        upload_section()
    if tab2:
        download_section()

with col2:
    get_query_section()