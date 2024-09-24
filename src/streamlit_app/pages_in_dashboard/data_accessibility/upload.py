import pandas as pd
import streamlit as st
import awswrangler as wr
from src.streamlit_app.pages_in_dashboard.data_accessibility.pandas_profiling_styling import custom_pandas_profiling_report 


# AWS Setup
bucket = "dssgx-munich-2024-bavarian-forest"
base_folder = "raw-data/bf_raw_files"


def write_csv_file_to_aws_s3(df: pd.DataFrame, path: str, **kwargs) -> None:
    """Writes a CSV file to AWS S3."""
    wr.s3.to_csv(df, path=path, **kwargs)

def generate_file_name(category: str, upload_timestamp: str) -> str:
    """Generates a file name based on the category."""
    return f"{category.replace(' ', '_')}_uploaded_{upload_timestamp}.csv"

def read_csv_file(uploaded_file):
    """Reads a CSV file uploaded by the user."""
    return pd.read_csv(uploaded_file, parse_dates=True, infer_datetime_format=True, low_memory=False)

def upload_section():
    st.header("Upload Data")

    # Select category
    category = st.selectbox(
    "Select the data category",
    ["visitor count sensors", "visitors count centers", "other"]
    )

    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file and category:
        data = read_csv_file(uploaded_file)

        # Display the header and place the upload button next to it
        st.write(" ")  # Add some space between elements
        col_preview, col_upload = st.columns([8, 2])

        with col_preview:
            st.header("Preview of Data")

        with col_upload:
            # Confirm button (aligned to the right side, bigger size)
            upload_confirm = st.button(
                label="Confirm Upload",
                disabled=not uploaded_file,
                help="Review the data before confirming upload",
            )
            st.write(f"<style>.stButton > button {{width: 100%; height: 50px;}}</style>", unsafe_allow_html=True)

        # Show the preview and summary report below the header
        st.dataframe(data)
        st.header("Data Summary Report")

        # Use the custom Pandas Profiling report function with the new theme
        custom_pandas_profiling_report(data)

        if upload_confirm:
            # Capture upload timestamp
            upload_timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')

            # Generate file name and S3 path
            file_name = generate_file_name(category, upload_timestamp)
            s3_path = f"s3://{bucket}/{base_folder}/{category.replace(' ', '_')}/{file_name}"

            # Upload the file to AWS S3
            write_csv_file_to_aws_s3(data, s3_path, index=False)
            st.success("File successfully uploaded.")