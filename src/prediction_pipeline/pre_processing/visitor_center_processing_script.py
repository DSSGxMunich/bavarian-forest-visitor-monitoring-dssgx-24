##################################################
# Package Import Section
##################################################
import pandas as pd  # Provides data structures and data analysis tools.
import numpy as np  # Supports large, multi-dimensional arrays and matrices.
import pyarrow as pa  # Provides functionalities for handling Apache Arrow data.
import pyarrow.parquet as pq  # Enables reading and writing Parquet files using PyArrow.
import awswrangler as wr
import boto3
import logging
import os


visitor_center_data_path = "s3://dssgx-munich-2024-bavarian-forest/raw-data/national-park-vacation-times-houses-opening-times-visitors.xlsx"
saved_path_visitor_center_query = "s3://dssgx-munich-2024-bavarian-forest/preprocessed_data/bf_preprocessed_files/visitor_centers/visitor_centers_2017_to_2024.parquet"
saved_path_visitor_center_modeling = "s3://dssgx-munich-2024-bavarian-forest/preprocessed_data/visitor_centers_hourly.parquet"

##########################################################################
##########################################################################
# Import raw data and Functions to Clean Data
##########################################################################
##########################################################################

boto3.setup_default_session(profile_name='anthony_garove_fellow_dssgx_24')

def source_data_from_aws_s3(path: str, **kwargs) -> pd.DataFrame:
    """Loads individual or multiple CSV files from an AWS S3 bucket.
    Args:
        path (str): The path to the CSV files on AWS S3.
        **kwargs: Additional arguments to pass to the read_csv function.
    Returns:
        pd.DataFrame: The DataFrame containing the data from the CSV files.
    """
    df = wr.s3.read_excel(path=path, **kwargs)
    return df

def change_binary_variables(df_visitcenters):
    # Documentation:
    # - This code converts columns in the DataFrame `df_visitcenters` that contain only binary values (0 and 1) to a boolean type.
    # - `df_visitcenters[column].isin([0, 1, np.nan]).all()` checks if all values in the column are either 0, 1, or NaN.
    # - `astype('bool')` converts the column from float64 type to boolean type, where 0 becomes False and 1 becomes True.
    # Iterate over each column in the DataFrame
    for column in df_visitcenters.columns:
        # Check if all values in the column are either 0, 1, or NaN
        if df_visitcenters[column].isin([0, 1, np.nan]).all():
            # Convert the column to boolean type (binary values: True, False)
            df_visitcenters[column] = df_visitcenters[column].astype('bool')

    return df_visitcenters

def change_object_variables(df_visitcenters):
    # Convert columns with object data type to category type
    # This is useful for categorical variables with more than 3 levels
    for col in df_visitcenters.select_dtypes(include=['object']).columns:
        df_visitcenters[col] = df_visitcenters[col].astype('category')

    return df_visitcenters

def change_to_numeric_types(df_visitcenters):
    # Convert specific columns to numeric type (float64)
    # Using 'errors="coerce"' will convert invalid parsing to NaN
    df_visitcenters['Parkpl_HEH_PKW'] = pd.to_numeric(df_visitcenters['Parkpl_HEH_PKW'], errors='coerce')
    df_visitcenters['Waldschmidthaus_geoeffnet'] = pd.to_numeric(df_visitcenters['Waldschmidthaus_geoeffnet'], errors='coerce')
    return df_visitcenters

def correct_and_convert_schulferien(df_visitcenters):
    """
    Corrects a typo in the 'Schulferien_Bayern' column and converts it to boolean type.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the 'Schulferien_Bayern' column.
    
    Returns:
    pandas.DataFrame: DataFrame with corrected 'Schulferien_Bayern' values and converted to boolean type.
    """
    # Correct the typo in specific value for column 'Schulferien_Bayern' (from `10` to `0`)
    df_visitcenters.loc[df_visitcenters['Datum'] == '2017-04-30', 'Schulferien_Bayern'] = 0
    
    # Change 'Schulferien_Bayern' to bool type
    df_visitcenters['Schulferien_Bayern'] = df_visitcenters['Schulferien_Bayern'].astype(bool)
    
    return df_visitcenters

def change_holidays_to_bool(df_visitcenters):
    # Convert specific columns representing binary variables to boolean type
    df_visitcenters['Schulferien_Bayern'] = df_visitcenters['Schulferien_Bayern'].astype(bool)
    df_visitcenters['Schulferien_CZ'] = df_visitcenters['Schulferien_CZ'].astype(bool)
    return df_visitcenters

def change_duplicate_date(df_visitcenters):
    # This changes the second instance of date 9-29-2021 to 9-29-2023
    indices = df_visitcenters[df_visitcenters['Datum'] == '9/29/2021'].index
    if len(indices) > 1:
    # Replace the second instance with '9/29/2023'
        df_visitcenters.at[indices[1], 'Datum'] = '9/29/2023'
    return df_visitcenters

def correct_besuchszahlen_heh(df):
    """
    Corrects the 'Besuchszahlen_HEH' column by rounding up values with non-zero fractional parts to the nearest whole number.
    Converts the column to Int64 type to retain NaN values.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the 'Besuchszahlen_HEH' column.
    
    Returns:
    pandas.DataFrame: DataFrame with 'Besuchszahlen_HEH' corrected and converted to Int64 type.
    """
    # Apply np.ceil() to round up values with non-zero fractional parts to nearest whole number
    df['Besuchszahlen_HEH'] = df['Besuchszahlen_HEH'].apply(
        lambda x: np.ceil(x) if pd.notna(x) and x % 1 != 0 else x
    )
    
    # Convert 'Besuchszahlen_HEH' to Int64 to retain NaN values
    df['Besuchszahlen_HEH'] = df['Besuchszahlen_HEH'].astype('Int64')
    
    return df

def correct_and_convert_wgm_geoeffnet(df):
    """
    Corrects the 'WGM_geoeffnet' column by replacing the value 11 with 1.
    Converts the column to boolean type.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the 'WGM_geoeffnet' column.
    
    Returns:
    pandas.DataFrame: DataFrame with 'WGM_geoeffnet' corrected and converted to boolean type.
    """
    # Replace single value of 11 with 1 in 'WGM_geoeffnet' column
    df['WGM_geoeffnet'] = df['WGM_geoeffnet'].replace(11, 1)
    
    # Convert 'WGM_geoeffnet' column to boolean type
    df['WGM_geoeffnet'] = df['WGM_geoeffnet'].astype(bool)
    
    return df

def remove_last_row_if_needed(df):
    """
    Removes the last row from the DataFrame if it has 2923 rows.
    
    Parameters:
    df (pandas.DataFrame): DataFrame to be checked and modified.
    
    Returns:
    pandas.DataFrame: Updated DataFrame with the last row removed if the initial length was 2923.
    """
    # Check if the DataFrame has exactly 2923 rows
    if len(df) == 2923:
        # Drop the last row
        df = df.iloc[:-1]
    
    return df

def clean_visitor_center_data(df_visitcenters):
    # Change boolean variables
    df_visitcenters=change_binary_variables(df_visitcenters)
    # Change object variables
    df_visitcenters=change_object_variables(df_visitcenters)
    # Change numeric variables
    df_visitcenters=change_to_numeric_types(df_visitcenters)
    # Correct Czech holiday value
    df_visitcenters=correct_and_convert_schulferien(df_visitcenters)
    # Change holidays to bool type
    df_visitcenters=change_holidays_to_bool(df_visitcenters)
    # Change duplicated date
    df_visitcenters=change_duplicate_date(df_visitcenters)
    # Correct Besuchszahlen counts to non-decimal (round up)
    df_visitcenters=correct_besuchszahlen_heh(df_visitcenters)
    # Correct WGM_geoffnet - instance of 11 (should be 1)
    df_visitcenters=correct_and_convert_wgm_geoeffnet(df_visitcenters)
    # Remove empty extra row
    df_visitcenters=remove_last_row_if_needed(df_visitcenters)

    return df_visitcenters

##########################################################################
##########################################################################
# Functions to Create New Variables/Columns
##########################################################################
##########################################################################

def add_date_variables(df):
    """
    Create new columns for day, month, and year from a date column in the DataFrame.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the 'Datum' column with date information.
    
    Returns:
    pandas.DataFrame: DataFrame with additional columns for day, month, and year.
    """
    # Convert 'Datum' column to datetime format
    df['Datum'] = pd.to_datetime(df['Datum'])
    
    # Add new columns for day, month, and year
    df['Tag'] = df['Datum'].dt.day
    df['Monat'] = df['Datum'].dt.month
    df['Jahr'] = df['Datum'].dt.year
    
    # Change data types for modeling purposes
    df['Tag'] = df['Tag'].astype('Int64')
    df['Monat'] = df['Monat'].astype('category')
    df['Jahr'] = df['Jahr'].astype('Int64')
    
    return df

def add_season_variable(df):
    """
    Create a new column 'Jahreszeit' in the DataFrame based on the month variable.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the 'Monat' column with month information.
    
    Returns:
    pandas.DataFrame: DataFrame with an additional 'Jahreszeit' column representing the season.
    """
    # Define the seasons based on the month
    df['Jahreszeit'] = df['Monat'].apply(
        lambda x: 'Frühling' if x in [3, 4, 5] else
                  'Sommer' if x in [6, 7, 8] else
                  'Herbst' if x in [9, 10, 11] else
                  'Winter' if x in [12, 1, 2] else
                  np.nan
    )
    
    # Convert the 'Jahreszeit' column to category type
    df['Jahreszeit'] = df['Jahreszeit'].astype('category')
    
    return df

def add_and_translate_day_of_week(df):
    """
    Create a new column 'Wochentag' that represents the day of the week in German.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the 'Datum' column with date information.
    
    Returns:
    pandas.DataFrame: DataFrame with updated 'Wochentag' column in German.
    """
    # Create a new column 'Wochentag2' with the day of the week in English
    df['Wochentag2'] = df['Datum'].dt.day_name()
    df['Wochentag2'] = df['Wochentag2'].astype('category')
    
    # Define the translation mapping from English to German
    translation_map = {
        'Monday': 'Montag',
        'Tuesday': 'Dienstag',
        'Wednesday': 'Mittwoch',
        'Thursday': 'Donnerstag',
        'Friday': 'Freitag',
        'Saturday': 'Samstag',
        'Sunday': 'Sonntag'
    }
    
    # Replace the English day names in the 'Wochentag2' column with German names
    df['Wochentag2'] = df['Wochentag2'].replace(translation_map)
    
    # Remove the 'Wochentag' column from the DataFrame
    df = df.drop(columns=['Wochentag'], errors='ignore')
    
    # Rename 'Wochentag2' to 'Wochentag'
    df = df.rename(columns={'Wochentag2': 'Wochentag'})
    
    return df

def add_weekend_variable(df):
    """
    Create a new binary column 'Wochenende' indicating whether the day is a weekend.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the 'Wochentag' column with German day names.
    
    Returns:
    pandas.DataFrame: DataFrame with an additional 'Wochenende' column indicating weekend status.
    """
    # Create a new binary column 'Wochenende' where True represents weekend days (Saturday, Sunday)
    df['Wochenende'] = df['Wochentag'].apply(lambda x: x in ['Samstag', 'Sonntag'])
    
    # Convert the 'Wochenende' column to boolean type
    df['Wochenende'] = df['Wochenende'].astype(bool)
    
    return df

def reorder_columns(df):
    """
    Reorder columns in the DataFrame to place date-related variables together.
    
    Parameters:
    df (pandas.DataFrame): DataFrame with various columns including date-related variables.
    
    Returns:
    pandas.DataFrame: DataFrame with columns reordered to place date-related variables next to each other.
    """
    # Define the desired order of columns
    column_order = [
        'Datum', 'Tag', 'Monat', 'Jahr', 'Wochentag', 'Wochenende', 'Jahreszeit', 'Laubfärbung',
        'Besuchszahlen_HEH', 'Besuchszahlen_HZW', 'Besuchszahlen_WGM', 
        'Parkpl_HEH_PKW', 'Parkpl_HEH_BUS', 'Parkpl_HZW_PKW', 'Parkpl_HZW_BUS', 
        'Schulferien_Bayern', 'Schulferien_CZ', 'Feiertag_Bayern', 'Feiertag_CZ', 
        'HEH_geoeffnet', 'HZW_geoeffnet', 'WGM_geoeffnet', 'Lusenschutzhaus_geoeffnet', 
        'Racheldiensthuette_geoeffnet', 'Waldschmidthaus_geoeffnet', 
        'Falkensteinschutzhaus_geoeffnet', 'Schwellhaeusl_geoeffnet', 'Temperatur', 
        'Niederschlagsmenge', 'Schneehoehe', 'GS mit', 'GS max'
    ]
    
    # Reorder columns in the DataFrame
    df = df[column_order]
    
    return df

def add_additional_columns(df_visitcenters):
    # Add date variables
    df_visitcenters=add_date_variables(df_visitcenters)
    # Add season variable
    df_visitcenters=add_season_variable(df_visitcenters)
    # Add day of week variable
    df_visitcenters=add_and_translate_day_of_week(df_visitcenters)
    # Add weekend variable dummy code
    df_visitcenters=add_weekend_variable(df_visitcenters)
    # Reorder columns to group similar variables
    df_visitcenters=reorder_columns(df_visitcenters)
    return df_visitcenters

##########################################################################
##########################################################################
# Functions to Handle Extreme Outliers
##########################################################################
##########################################################################

def detect_outliers_std(df, column, num_sd=7):
    """
    Detect outliers in a specific column of the DataFrame using the standard deviation method.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the column to check.
    column (str): Name of the column to check for outliers.
    num_sd (int): Number of standard deviations to define the outlier bounds (default is 7).
    
    Returns:
    pandas.DataFrame: DataFrame containing rows with outliers in the specified column.
    """
    mean = df[column].mean()
    std_dev = df[column].std()
    
    # Define the bounds for outliers
    lower_bound = mean - num_sd * std_dev
    upper_bound = mean + num_sd * std_dev
    
    # Identify outliers
    outliers_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    return df[outliers_mask][['Datum', column]]

def handle_outliers(df, num_sd=7):
    """
    Detect and handle outliers for a list of columns by replacing them with NaN.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the columns to check.
    num_sd (int): Number of standard deviations to define the outlier bounds (default is 7).
    
    Returns:
    pandas.DataFrame: DataFrame with outliers replaced by NaN in the specified columns.
    """
    columns = [
    'Besuchszahlen_HEH',
    'Besuchszahlen_HZW',
    'Besuchszahlen_WGM',
    'Parkpl_HEH_PKW',
    'Parkpl_HEH_BUS',
    'Parkpl_HZW_PKW',
    'Parkpl_HZW_BUS']
    
    #outliers = {}
    
    # Detect outliers and store in dictionary
    #for column in columns:
        #outliers[column] = detect_outliers_std(df, column, num_sd)
    
    # Handle outliers by replacing with NaN
    for column in columns:
        mean = df[column].mean()
        std_dev = df[column].std()
        lower_bound = mean - num_sd * std_dev
        upper_bound = mean + num_sd * std_dev
        df.loc[(df[column] < lower_bound) | (df[column] > upper_bound), column] = np.nan
    
    return df

##########################################################################
##########################################################################
# Create an hourly level DataFrame by expanding each day into 24 hours

# This hourly data frame is later joined with other data for predictions
##########################################################################
##########################################################################

def create_hourly_dataframe(df):
    """
    Expands the daily data in the DataFrame to an hourly level by duplicating each day into 24 hourly rows.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing daily data with a 'Datum' column representing dates.
    
    Returns:
    pandas.DataFrame: New DataFrame with an hourly level where each day is expanded into 24 hourly rows.
    """
    # Generate a new DataFrame where each day is expanded into 24 rows (one per hour)
    df_hourly = df.loc[df.index.repeat(24)].copy()
    
    # Create the hourly timestamps by adding hours to the 'Datum' column
    df_hourly['Datum'] = df_hourly['Datum'] + pd.to_timedelta(df_hourly.groupby(df_hourly.index).cumcount(), unit='h')
    
    # Rename columns for clarity
    df_hourly = df_hourly.rename(columns=lambda x: x.strip())
    df_hourly = df_hourly.rename(columns={'Datum': 'Time'})
    
    return df_hourly

def rename_and_set_time_as_index(df):
    """
    Rename columns, convert 'time' column to datetime, and set 'time' as the index.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing data with a 'Datum' column to be renamed and converted.
    
    Returns:
    pandas.DataFrame: The cleaned DataFrame with 'Datum' renamed to 'time', converted to datetime, and 'time' set as index.
    """
    # Rename 'Datum' column to 'time'
    df.rename(columns={'Datum': 'time'}, inplace=True)
    df.index=pd.to_datetime(df.index)

    # Convert 'time' column to datetime
    #df['time'] = pd.to_datetime(df['time'])
    
    # Set 'time' column as index
    #df.set_index('time', inplace=True)
    
    return df

def write_parquet_file_to_aws_s3(df: pd.DataFrame, path: str, **kwargs) -> pd.DataFrame:
    """Writes an individual Parquet file to AWS S3.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        path (str): The path to the Parquet files on AWS S3.
        **kwargs: Additional arguments to pass to the to_parquet function.
    """
    try:
        wr.s3.to_parquet(df, path=path, **kwargs)
        print(f"DataFrame successfully written to {path}")
    except Exception as e:
        logging.error(f"Failed to write DataFrame to S3. Error: {e}")
    return



def get_visitor_center_data():
    sourced_df = source_data_from_aws_s3(visitor_center_data_path)
    cleaned_df = clean_visitor_center_data(sourced_df)
    transformed_df = add_additional_columns(cleaned_df)
    daily_df = handle_outliers(transformed_df)
    hourly_df = create_hourly_dataframe(daily_df)
    hourly_df = rename_and_set_time_as_index(hourly_df)
    # Save to AWS
    # Save daily data to AWS for querying
    write_parquet_file_to_aws_s3(daily_df, saved_path_visitor_center_query)
    # Save houly data to AWS for joining/modeling
    write_parquet_file_to_aws_s3(hourly_df, saved_path_visitor_center_modeling)




if __name__ == '__main__':
    get_visitor_center_data()