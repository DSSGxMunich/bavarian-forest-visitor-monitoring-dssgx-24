import streamlit as st
import awswrangler as wr
import pandas as pd


# AWS Setup
bucket = "dssgx-munich-2024-bavarian-forest"
base_folder = "raw-data/bf_raw_files"

def list_files_in_s3(category: str) -> list:
    """Lists files in S3 for a given category and returns only file names."""
    s3_prefix = f"{base_folder}/{category.replace(' ', '_')}"
    full_paths = wr.s3.list_objects(f"s3://{bucket}/{s3_prefix}/")
    return [path.split('/')[-1] for path in full_paths]  # Extract only the file names

def load_csv_files_from_aws_s3(path: str, **kwargs) -> pd.DataFrame:
    """Loads individual or multiple CSV files from an AWS S3 bucket."""
    df = wr.s3.read_csv(path=path, **kwargs)


def download_section():

    st.header("Download Data")
        
    # Select category
    category = st.selectbox(
        "Select the data category to browse",
        ["visitor count sensors", "visitors count centers", "other"]
    )
    
    # List files based on category
    if category:
        files = list_files_in_s3(category)
        selected_file = st.selectbox("Select a file to preview", files) if files else None

        if selected_file:
            # Preview button (enabled only when a file is selected)
            preview_confirm = st.button(
                label="Preview Data",
                disabled=not selected_file,
                help="Preview the data before confirming download"
            )

            if preview_confirm:
                # Correctly construct the full path to the selected file
                file_path = f"s3://{bucket}/{base_folder}/{category.replace(' ', '_')}/{selected_file}"

                # Load and preview selected file
                st.write(f"Preview of {selected_file}")
                data = load_csv_files_from_aws_s3(file_path)
                st.dataframe(data)

                # Download button
                st.download_button(
                    label="Download selected file as CSV",
                    data=data.to_csv(index=False),
                    file_name=selected_file,
                    mime='text/csv',
                )