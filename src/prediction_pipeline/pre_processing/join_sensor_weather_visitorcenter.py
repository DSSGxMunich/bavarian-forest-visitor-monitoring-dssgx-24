"""
Join sensor, weather and visitor center data script.

This script sources from AWS three different data sources, join them over a datetime index, and writes the joined df as a csv to AWS.

Usage:
- Change the global variables section if needed
    - Fill your AWS credentiales
    - Change the data paths or output directories

- Run the script:

  $ python src/join_sensor_weather_visitorcenter.py

Output:
- The joined data is saved as 'joined_sensor_weather_visitorcenter_2016-2024.csv' in the 'preprocessed_data' directory in AWS.
"""


import pandas as pd
from functools import reduce
import awswrangler as wr

###########################################################################################
#GLOBAL VARIABLES
###########################################################################################


sensor_aws_path = 's3://dssgx-munich-2024-bavarian-forest/preprocessed_data/normalized_visitor_sensor_data_2016_2024.csv'
weather_aws_path = 's3://dssgx-munich-2024-bavarian-forest/preprocessed_data/processed_weather_data_2016-24_forecasted_imputed.csv'
visitorcenter_aws_path = 's3://dssgx-munich-2024-bavarian-forest/preprocessed_data/bf_visitcenters_hourly .csv'

output_file_name = "joined_sensor_weather_visitorcenter_2016-2024.csv"
output_bucket = "dssgx-munich-2024-bavarian-forest"
output_data_folder = "preprocessed_data"

timestamp_column = "Time" # name of column with timestamp in the dataframes

##############################################################################################

##############################################################################################

# Functions

def load_csv_files_from_aws_s3(path: str, **kwargs) -> pd.DataFrame:
    """Loads individual or multiple CSV files from an AWS S3 bucket.

    Args:
        path (str): The path to the CSV files on AWS S3.
        **kwargs: Additional arguments to pass to the read_csv function.

    Returns:
        pd.DataFrame: The DataFrame containing the data from the CSV files.
    """

    df = wr.s3.read_csv(path=path, **kwargs)
    return df

def create_datetimeindex(df, timestamp_column):
    """
    Prepare DataFrame by ensuring the index is a DateTimeIndex, resampling to hourly frequency,
    and handling missing values.
    
    Parameters:
    - df: DataFrame containing the data.
    - timestamp_column: Name of the timestamp column to convert and set as the index.
    
    Returns:
    - df: DataFrame resampled to hourly frequency with missing values handled.
    """
    # Ensure the timestamp column is converted to datetime if it's not already the index
    if timestamp_column in df.columns:
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
        df.set_index(timestamp_column, inplace=True)
    
    # Ensure the index is a DateTimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("Index must be a DateTimeIndex.")
    
    return df

def write_csv_file_to_aws_s3(df: pd.DataFrame, path: str, **kwargs) -> pd.DataFrame:
    """Writes an individual CSV file to AWS S3.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        path (str): The path to the CSV files on AWS S3.
        **kwargs: Additional arguments to pass to the to_csv function.
    """

    wr.s3.to_csv(df, path=path, **kwargs)
    return


def main():

    # Load each dataset and creates a list for further loops
    sensor_df = load_csv_files_from_aws_s3(sensor_aws_path)
    weather_df = load_csv_files_from_aws_s3(weather_aws_path)
    visitorcenter_df = load_csv_files_from_aws_s3(visitorcenter_aws_path)

    df_list = [sensor_df, weather_df, visitorcenter_df]

    # Iterate over list of df to create datetime index
    for df in df_list:
        create_datetimeindex(df, timestamp_column)

    # Perform an outer join on datasets,
    # this ensures that all indices from both DataFrames will be included in the final result.
    # If an index doesn't exist in one of the DataFrames, the resulting cells will be filled with NaN.

    joined_data = reduce(lambda left, right: pd.concat([left, right], axis=1, join='outer'), df_list) 

    write_csv_file_to_aws_s3(
    df=joined_data,
    path=f"s3://{output_bucket}/{output_data_folder}/{output_file_name}",
    )
    
    print("Joined data uploaded to AWS succesfully!")
    
if __name__ == "__main__":
    main()