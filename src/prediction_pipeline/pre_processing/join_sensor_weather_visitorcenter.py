"""
Join sensor, weather and visitor center data script.

This script sources  three different data sources, joins them over a datetime index, and returns the joined data to be used for the model.

Usage:

- Run the script:

  $ python src/join_sensor_weather_visitorcenter.py
"""
import pandas as pd
from functools import reduce


###########################################################################################

# Functions

def create_datetimeindex(df):
    """
    Prepare DataFrame by ensuring the index is a DateTimeIndex, resampling to hourly frequency,
    and handling missing values.
    
    Parameters:
    - df: DataFrame containing the data.
    - "Time": Name of the timestamp column to convert and set as the index.
    
    Returns:
    - df: DataFrame resampled to hourly frequency with missing values handled.
    """
    # Ensure the timestamp column is converted to datetime if it's not already the index

    df["Time"] = pd.to_datetime(df["Time"])
    df.set_index("Time", inplace=True)
    
    # Ensure the index is a DateTimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("Index must be a DateTimeIndex.")
    
    return df

def join_dataframes(df_list) -> pd.DataFrame:
    """
    Joins a list of DataFrames using an outer join along the columns.

    Args:
        df_list (list of pd.DataFrame): A list of pandas DataFrames to join.

    Returns:
        pd.DataFrame: A single DataFrame resulting from concatenating all input DataFrames along columns.
    """
    return reduce(lambda left, right: pd.concat([left, right], axis=1, join='outer'), df_list)


def get_joined_dataframe(weather_data, visitor_count_data, visitorcenter_data) -> pd.DataFrame:
    """
    Main function to run the data joining pipeline.

    This function loads the visitor count, visitor center and weather data, preprocesses them and joins them into one dataframe.

    Returns:
        pd.DataFrame: The joined data.
    """
    df_list = [weather_data, visitor_count_data, visitorcenter_data]
    for df in df_list:
        create_datetimeindex(df)

    joined_data = join_dataframes(df_list)

    return joined_data
