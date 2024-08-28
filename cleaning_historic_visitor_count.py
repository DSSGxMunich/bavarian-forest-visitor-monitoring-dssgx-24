#import libraries

import pandas as pd
import locale
import glob
import chardet
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import awswrangler as wr
import boto3
"""



LOAD PREPROCESSED DATA FROM AWS


"""

df = visitor_counts_parsed_dates.reset_index(drop=True)

#lists and dictionaries for columns that need to be dropped or renamed

to_drop = ['Brechhäuslau Fußgänger IN', 'Brechhäuslau Fußgänger OUT', 'Waldhausreibe Channel 1 IN', 'Waldhausreibe Channel 2 OUT']

to_rename = {'Bucina IN': 'Bucina PYRO IN',
          'Bucina OUT': 'Bucina PYRO OUT',
          'Gsenget IN.1': 'Gsenget Fußgänger IN',
          'Gsenget OUT.1': 'Gsenget Fußgänger OUT',
          'Gfäll Fußgänger IN' : 'Gfäll IN',
          'Gfäll Fußgänger OUT': 'Gfäll OUT',
          'Fredenbrücke Fußgänger IN' : 'Fredenbrücke IN',
          'Fredenbrücke Fußgänger OUT': 'Fredenbrücke OUT',
          'Diensthüttenstraße Fußgänger IN': 'Diensthüttenstraße IN' ,
          'Diensthüttenstraße Fußgänger OUT': 'Diensthüttenstraße OUT',
          'Racheldiensthütte Cyclist OUT' : 'Racheldiensthütte Fahrräder OUT',
          'Racheldiensthütte Pedestrian IN' : 'Racheldiensthütte Fußgänger IN',
          'Racheldiensthütte Pedestrian OUT' : 'Racheldiensthütte Fußgänger OUT',
          'Sagwassersäge Fußgänger IN' : 'Sagwassersäge IN',
          'Sagwassersäge Fußgänger OUT': 'Sagwassersäge OUT',
          'Schwarzbachbrücke Fußgänger IN' : 'Schwarzbachbrücke IN',
          'Schwarzbachbrücke Fußgänger OUT' : 'Schwarzbachbrücke OUT',
          'NPZ_Falkenstein IN' : 'Falkenstein 1 PYRO IN',
          'NPZ_Falkenstein OUT' : 'Falkenstein 1 PYRO OUT',
          'TFG_Falkenstein_1 Fußgänger zum Parkplatz' : 'Falkenstein 1 OUT',
          'TFG_Falkenstein_1 Fußgänger zum HZW' : 'Falkenstein 1 IN',
          'TFG_Falkenstein_2 Fußgänger In Richtung Parkplatz' : 'Falkenstein 2 OUT',
          'TFG_Falkenstein_2 Fußgänger In Richtung TFG' : 'Falkenstein 2 IN',
          'TFG_Lusen IN' : 'Lusen 1 PYRO IN',
          'TFG_Lusen OUT' : 'Lusen 1 PYRO OUT',
          'TFG_Lusen_1 Fußgänger Richtung TFG': 'Lusen 1 EVO IN',
          'TFG_Lusen_1 Fußgänger Richtung Parkplatz' : 'Lusen 1 EVO OUT',
          'TFG_Lusen_2 Fußgänger Richtung Vögel am Waldrand': 'Lusen 2 IN',
          'TFG_Lusen_2 Fußgänger Richtung Parkplatz' : 'Lusen 2 OUT',
          'TFG_Lusen_3 TFG Lusen 3 IN': 'Lusen 3 IN',
          'TFG_Lusen_3 TFG Lusen 3 OUT': 'Lusen 3 OUT',
          'Waldspielgelände_1 IN': 'Waldspielgelände IN',
          'Waldspielgelände_1 OUT': 'Waldspielgelände OUT',
          'Wistlberg Fußgänger IN' : 'Wistlberg IN',
          'Wistlberg Fußgänger OUT' : 'Wistlberg OUT',
          'Trinkwassertalsperre IN' : 'Trinkwassertalsperre PYRO IN', 
          'Trinkwassertalsperre OUT' : 'Trinkwassertalsperre PYRO OUT'
          }

def fix_columns_names(df, rename, drop, create):
    """
    Processes the given DataFrame by renaming columns, dropping specified columns, and creating a new column for Bucina_Multi IN by summing the Bucina_Multi Fahrräder IN and Bucina_Multi Fußgänger IN columns. .

    Args:
        df (pd.DataFrame): The DataFrame to be modified.
        rename (dict): A dictionary where the keys are existing column names and the values are the new column names.
        drop (list): A list of column names that should be removed from the DataFrame.
        create (str): The name of the new column that will be created by summing the "Bucina_Multi Fahrräder IN" 
                      and "Bucina_Multi Fußgänger IN" columns.

    Returns:
        pd.DataFrame: The modified DataFrame with the specified changes applied.
    """
    # Rename columns according to the provided mapping
    df.rename(columns=rename, inplace=True)
    print(len(rename), ' columns were renamed')

    # Remove the specified columns from the DataFrame
    df.drop(columns=drop, inplace=True)
    print(len(drop), ' repeated columns were dropped')

    # Add a new column by summing two existing columns
    df['Bucina_Multi IN'] = df["Bucina_Multi Fahrräder IN"] + df["Bucina_Multi Fußgänger IN"]
    print('Bucina_Multi IN column was created')

    return df


# Fix problems with duplicated values in time column

def correct_and_impute_times(df):
    
    """
    Corrects repeated timestamps caused by a 2-hour interval that is indicative of a daylight saving.

    The function operates under the following assumptions:
    1. The first interval in the 'Time' column is considered the reference interval.
    2. If any subsequent intervals differ from this reference, particularly showing a 2-hour difference due to daylight saving changes, the repeated timestamp is corrected by subtracting one hour.
    3. The data values for the corrected timestamp are then imputed from the next available row.

    Args:
        df (pandas.DataFrame): A DataFrame containing a 'Time' column with datetime-like values and other associated data columns.

    Returns:
        pandas.DataFrame: The corrected DataFrame with timestamps set as the index and sorted chronologically.

    Raises:
        ValueError: If the 'Time' column is missing from the DataFrame.
        KeyError: If an index out of range occurs due to imputation attempts beyond the DataFrame bounds.
    """
    # Calculate time intervals
    intervals = df.Time.diff().dropna()
    reference_interval = intervals.iloc[0]  # Establish the first interval as the reference

    # Identify intervals that differ from the reference interval
    different_intervals = intervals[intervals != reference_interval]

    # Identify the indexes for intervals of 2 hours (indicative of a daylight saving time change)
    index_wrong_time = different_intervals[different_intervals == "0 days 02:00:00"].index

    # Impute values from the next row for affected timestamps
    for idx in index_wrong_time:
        df.loc[idx, 'Time'] = df.loc[idx, 'Time'] - pd.Timedelta(hours=1)  # Adjust the repeated timestamp by subtracting one hour
        df.loc[idx, df.columns != 'Time'] = df.loc[idx + 1, df.columns != 'Time']  # Impute the values from the next row

    # Set 'Time' as the index and sort the DataFrame by index
    df = df.set_index('Time').sort_index()

    return df

def correct_non_replaced_sensors(df):
    """
    Replaces data with NaN for non-replaced sensors in the DataFrame based on specified timestamps. A dictionary is provided where keys are timestamps as strings and values are lists of column names that should be set to NaN if the index is earlier than the timestamp.

    Args:
        df (pd.DataFrame): The DataFrame to be corrected.

    Returns:
        pd.DataFrame: The DataFrame with corrected sensor data.
    """

    dict_non_replaced = {'2020-07-30 00:00:00' : ['Lusen 1 PYRO IN', 'Lusen 1 PYRO OUT'],
                     '2022-12-20 00:00:00' : ['Lusen 3 IN', 'Lusen 3 OUT'],
                     '2022-10-12 00:00:00' : ['Gsenget IN', 'Gsenget OUT']}


    # Iterate over the dictionary of non-replaced sensors
    for key, columns in dict_non_replaced.items():
        # Convert the timestamp key from string to datetime object
        timestamp = pd.to_datetime(key)
        
        # Set values to NaN for specified columns where the index is earlier than the given timestamp
        df.loc[df.index < timestamp, columns] = np.nan

    print("Out of place values were turn to NaN for Lusen 1 PYRO, Lusen 3 and Gsenget")    

    return df


# Fix overlapping values in replaced sensors

def correct_overlapping_sensor_data(df):
    """
    Corrects sensor overlapping data by setting specific values to NaN based on replacement dates. Also filters the DataFrame to include only rows with an index timestamp on or after "2016-05-10 03:00:00". This is 3am after the installing date for the first working sensor.

    Args:
        df (pd.DataFrame): The DataFrame containing sensor data to be corrected.

    Returns:
        pd.DataFrame: The DataFrame with corrected sensor data.
    """
    # Define the replacement dates and columns for different sensor types
    replacement_dates = {
        'trinkwassertalsperre': '2021-06-18 00:00:00',
        'bucina': '2021-05-28 00:00:00',
        'falkenstein 1': '2022-12-22 12:00:00'
    }

    multi_columns_dict = {
        'trinkwassertalsperre': [
            'Trinkwassertalsperre_MULTI Fußgänger IN',
            'Trinkwassertalsperre_MULTI Fußgänger OUT',
            'Trinkwassertalsperre_MULTI Fahrräder IN',
            'Trinkwassertalsperre_MULTI Fahrräder OUT',
            'Trinkwassertalsperre_MULTI IN',
            'Trinkwassertalsperre_MULTI OUT'
        ],
        'bucina': [
            'Bucina_Multi OUT',
            'Bucina_Multi Fußgänger IN',
            'Bucina_Multi Fahrräder IN',
            'Bucina_Multi Fahrräder OUT',
            'Bucina_Multi Fußgänger OUT',
            'Bucina_Multi IN'
        ],
        'falkenstein 1': [
            'Falkenstein 1 OUT',
            'Falkenstein 1 IN'
        ]
    }

    pyro_columns_dict = {
        'trinkwassertalsperre': [
            'Trinkwassertalsperre PYRO IN',
            'Trinkwassertalsperre PYRO OUT'
        ],
        'bucina': [
            'Bucina PYRO IN',
            'Bucina PYRO OUT'
        ],
        'falkenstein 1': [
            'Falkenstein 1 PYRO IN',
            'Falkenstein 1 PYRO OUT'
        ]
    }

    # Process each sensor type based on the predefined dictionaries
    for sensor_type in replacement_dates:
        replacement_date = pd.to_datetime(replacement_dates[sensor_type])
        multi_columns = multi_columns_dict.get(sensor_type, [])
        pyro_columns = pyro_columns_dict.get(sensor_type, [])

        # Set to NaN the values in 'multi_columns' for dates on or before the replacement date
        if multi_columns:
            df.loc[df.index <= replacement_date, multi_columns] = np.nan

        # Set to NaN the values in 'pyro_columns' for dates after the replacement date
        if pyro_columns:
            df.loc[df.index > replacement_date, pyro_columns] = np.nan

    # Slice data before date because  there were no sensors installed
    df = df[df.index >= "2016-05-10 03:00:00"]


    print("Fixed overlapping values for replaced sensors")
    return df


def merge_columns(df):
    """
    Merges columns from replaced sensors in the DataFrame into new combined columns based on a predefined mapping and drops the original columns after merging.

    The function merges multiple related columns into single combined columns using a predefined dictionary (`merge_dict`). 
    For each key-value pair in the dictionary, values from the first column are used, and missing values are filled 
    from the second column. After merging, the original columns used for merging are dropped from the DataFrame.

    Args:
        df (pandas.DataFrame): A DataFrame containing columns to be merged.

    Returns:
        pandas.DataFrame: The modified DataFrame with the new merged columns and original columns removed.
    """
    merge_dict = {
        'Bucina MERGED IN': ['Bucina PYRO IN', 'Bucina_Multi IN'],
        'Bucina MERGED OUT': ['Bucina PYRO OUT', 'Bucina_Multi OUT'],
        'Falkenstein 1 MERGED IN': ['Falkenstein 1 PYRO IN', 'Falkenstein 1 IN'],
        'Falkenstein 1 MERGED OUT': ['Falkenstein 1 PYRO OUT', 'Falkenstein 1 OUT'],
        'Lusen 1 MERGED IN': ['Lusen 1 PYRO IN', 'Lusen 1 EVO IN'],
        'Lusen 1 MERGED OUT': ['Lusen 1 PYRO OUT', 'Lusen 1 EVO OUT'],
        'Trinkwassertalsperre MERGED IN': ['Trinkwassertalsperre PYRO IN', 'Trinkwassertalsperre_MULTI IN'],
        'Trinkwassertalsperre MERGED OUT': ['Trinkwassertalsperre PYRO OUT', 'Trinkwassertalsperre_MULTI OUT']
    }

    # Iterate over each item in the dictionary to merge columns
    for new_col, cols in merge_dict.items():
        # Combine the two columns into one using the first non-null value
        df[new_col] = df[cols[0]].combine_first(df[cols[1]])

    # Drop the original columns used for merging
    cols_to_drop = [col for cols in merge_dict.values() for col in cols]
    df = df.drop(columns=cols_to_drop)

    return df

def handle_outliers(df):
    """
    Transform to NaN every value higher than 800. During exploration we found that values over that are outliers. There were only 6 rows with any count over 800

    Args:
        df (pandas.DataFrame): DataFrame with values to be turned to NaN.

    Returns:
        pandas.DataFrame: The modified DataFrame with values over 800 turned to NaN
    """

    df[df > 800] = np.nan

    return df

def traffic_columns_counting_sensors(df):
    """
    Discards columns with the distinction between cyclist and pedestrians, as they will not be taken into account this iteration. Adds a column to the DataFrame that counts the number of non-null entries in columns to determine the number of working sensors.


    Args:
        df (pandas.DataFrame): DataFrame containing the sensor data with various columns.

    Returns:
        pandas.DataFrame: The DataFrame with out cyclist and pedestrian columns and with an additional 'working_sensors' column that represents the count of non-null values in the relevant sensor columns for each row.
    """
    # Identify columns that do not include "Fahrräder" or "Fußgänger" in their names
    non_cyclist_pedestrian = [col for col in df.columns 
                             if "Fahrräder" not in col 
                             and "Fußgänger" not in col]
    
    # Discard columns with the distinction between cyclist and pedestrians    
    df = df[non_cyclist_pedestrian]

    # Count non-null entries in the identified columns and create a new column 'working_sensors'
    df['working_sensors'] = df[non_cyclist_pedestrian].notnull().sum(axis=1)

    return df


def calculate_traffic_metrics_abs(df):
    """
      This function calculates several traffic metrics and adds them to the DataFrame:
    - `traffic_abs`: The sum of all INs and OUTs for every sensor
    - `sum_IN_abs`: The sum of all columns containing 'IN' in their names.
    - `sum_OUT_abs`: The sum of all columns containing 'OUT' in their names.
    - `diff_abs`: The difference between `sum_IN_abs` and `sum_OUT_abs`.
    - `occupancy_abs`: The cumulative sum of `diff_abs`, representing the occupancy over time.

    Args:
        df (pandas.DataFrame): DataFrame containing traffic data.

    Returns:
        pandas.DataFrame: The DataFrame with additional columns for absolute traffic metrics.
    """
    # Calculate total traffic
    df["traffic_abs"] = df.sum(axis=1)

    # Calculate sum of 'IN' columns
    df["sum_IN_abs"] = df.filter(like='IN').sum(axis=1)

    # Calculate sum of 'OUT' columns
    df["sum_OUT_abs"] = df.filter(like='OUT').sum(axis=1)

    # Calculate difference between 'IN' and 'OUT' sums
    df['diff_abs'] = df['sum_IN_abs'] - df['sum_OUT_abs']

    # Calculate cumulative occupancy
    df['occupancy_abs'] = df['diff_abs'].cumsum().fillna(0)

    return df


def normalize_traffic_metrics(df):
    """
    Identifies change points and normalizes 'traffic' and 'occupancy' columns for each segment.

    This function performs the following steps:
    1. Identifies change points in the 'working_sensors' column to segment the data.
    2. Normalizes the columns 'traffic_abs', 'sum_IN_abs', 'sum_OUT_abs', 'diff_abs', and 'occupancy_abs'
       from 0% to 100% for each segment. The normalized values are stored in new columns with '_norm' suffixes.

    Args:
        df (pandas.DataFrame): DataFrame containing the traffic and occupancy metrics.

    Returns:
        pandas.DataFrame: The DataFrame with additional columns for normalized metrics.
    """
    # Step 1: Identify the change points
    change_points = df['working_sensors'].ne(df['working_sensors'].shift()).cumsum()

       # Initialize the scaler
    scaler = MinMaxScaler(feature_range=(0, 100))

    # Define dictionary mapping original column names to normalized column names
    metrics_dict = {
        'traffic_abs': 'traffic_norm',
        'sum_IN_abs': 'sum_IN_norm',
        'sum_OUT_abs': 'sum_OUT_norm',
        'diff_abs': 'diff_norm',
        'occupancy_abs': 'occupancy_norm'
    }

    # Normalize columns for each segment
    for segment in change_points.unique():
        segment_df = df[change_points == segment]
        
        # Fit and transform the segment data
        for key, value in metrics_dict.items():
            values = segment_df[[key]].values  # Extract values as a 2D array
            if len(values) > 1:  # Only scale if there is more than one value to avoid errors
                scaled_values = scaler.fit_transform(values)
                df.loc[segment_df.index, value] = scaled_values.flatten()

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

    df_mapped = fix_columns_names(df, rename=to_rename, drop=to_drop)
    
    df_imputed_timestamps = correct_and_impute_times(df_mapped)

    df_corrected_sensors = correct_non_replaced_sensors(df_imputed_timestamps)

    df_corrected_sensors = correct_overlapping_sensor_data(df_corrected_sensors)

    df_merged_columns = merge_columns(df_corrected_sensors)

    df_no_outliers = handle_outliers(df_merged_columns)

    df_traffic_columns = traffic_columns_counting_sensors(df_no_outliers)

    df_traffic_metrics = calculate_traffic_metrics_abs(df_traffic_columns)

    df_normalized_traffic = normalize_traffic_metrics(df_traffic_metrics)

    print("\n Visitor sensors data is preprocessed and traffic metrics are created! \n")

    write_csv_file_to_aws_s3(
        df=joined_data,
        path=f"s3://{output_bucket}/{output_data_folder}/{output_file_name}",
        )
    
    print("Preprocessed data uploaded to AWS succesfully!")





    print("")
    
if __name__ == "__main__":
    main()