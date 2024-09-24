
"""
Weather Data Sourcing

This script retrieves hourly weather data (Precipitation, Temperature, Wind Speed, Relative Humidity, and Sunshine Duration) for the Bavarian Forest region from the Meteostat API, and saves the processed data to a CSV file.

Usage:
- To run this script, simply execute it using Python:
  $ python src/weather_data_sourcing_and_processing.py
- The script will automatically fetch weather data for the specified date range, process it, and save it to a CSV file.
- Please change the AWS credentials, global variables (start and end time, latitude, and longitude), and the S3 bucket and folder name before running the script.

Output:
- The sourced and processed weather data is saved as '/sourced_weather_data_2016-24_non_imputed.csv' and '/processed_weather_data_2016-24_imputed.csv' in the 'preprocessed_data' folder 
    in the 'dssgx-munich-2024-bavarian-forest' AWS S3 bucket.

"""

# Import necessary libraries
import warnings
from datetime import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
from meteostat import Point, Hourly
import awswrangler as wr
from impute_missing_weather_values import fill_missing_values
from impute_missing_weather_values import fill_missing_values


# Ignore warnings
warnings.filterwarnings('ignore')


############################################################################################################
# Define global variables
############################################################################################################
# Uncomment this if you want to get the weather data for the next 7 days starting from today
# Get dates for the data sourcing
# START_TIME = datetime.now()
# END_TIME = (START_TIME + pd.Timedelta(days=7))

# Set time period for sourcing the data
START_TIME = datetime(2016, 1, 1)
END_TIME = datetime(2024, 9, 3)

# Coordinates of the Bavarian Forest (Haselbach)
# These coordinates are based on the weather recommendation by Google for a Bavarian Forest Weather search
LATITUDE = 49.31452390542327
LONGITUDE = 12.711573421032

# Set up S3 bucket and folder
bucket = "dssgx-munich-2024-bavarian-forest"
preprocessed_data_folder = "preprocessed_data"

############################################################################################################
# Define functions
############################################################################################################

def get_hourly_data(region):
    """
    Fetch hourly weather data for a specified region and date range.

    This function retrieves hourly weather data from the Meteostat API or another defined source,
    returning it as a pandas DataFrame.

    Args:
        region (Point): A `Point` object representing the geographical location (latitude, longitude).
        start_date (datetime): The start date for data retrieval.
        end_date (datetime): The end date for data retrieval.

    Returns:
        pandas.DataFrame: A DataFrame containing hourly weather data with the following columns:
            - time: Datetime of the record.
            - temp: Temperature in degrees Celsius.
            - dwpt: Dew point in degrees Celsius.
            - prcp: Precipitation in millimeters.
            - wdir: Wind direction in degrees.
            - wspd: Wind speed in km/h.
            - wpgt: Wind gust in km/h.
            - pres: Sea-level air pressure in hPa.
            - tsun: Sunshine duration in minutes.
            - snow: Snowfall in millimeters.
            - rhum: Relative humidity in percent.
            - coco: Weather condition code.
    """
    # Fetch hourly data
    data = Hourly(region, START_TIME, END_TIME).fetch()
    
    # Reset the index
    data.reset_index(inplace=True)
    return data


def process_hourly_data(data):
    """
    Process raw hourly weather data by cleaning and formatting.

    This function drops unnecessary columns, renames the remaining columns to more descriptive names,
    and converts the 'time' column to a datetime format.

    Args:
        data (pandas.DataFrame): A DataFrame containing raw hourly weather data.

    Returns:
        pandas.DataFrame: A DataFrame containing the processed hourly weather data with the following columns:
            - Time: Datetime of the record.
            - Temperature (°C): Temperature in degrees Celsius.
            - Precipitation (mm): Precipitation in millimeters.
            - Wind Speed (km/h): Wind speed in km/h.
            - Sunshine Duration (min): Duration of sunshine in minutes.
            - Relative Humidity (%): Relative humidity in percent.
    """
    # Drop unnecessary columns
    data = data.drop(columns=['dwpt', 'snow', 'wdir', 'wpgt', 'pres', 'coco'])

    # Rename columns for clarity
    data = data.rename(columns={
        'time': 'Time',
        'temp': 'Temperature (°C)',
        'prcp': 'Precipitation (mm)',
        'wspd': 'Wind Speed (km/h)',
        'tsun': 'Sunshine Duration (min)',
        'rhum': 'Relative Humidity (%)'
    })

    # Convert the 'Time' column to datetime format
    data['Time'] = pd.to_datetime(data['Time'])
    return data


def save_data_to_csv(data, save_path):
    """
    Save processed weather data to a CSV file.

    This function saves the processed DataFrame to a specified directory. If the directory does not exist,
    it will be created.

    Args:
        data (pandas.DataFrame): A DataFrame containing the processed hourly weather data.
        save_path (str): The directory path where the CSV file will be saved.

    Returns:
        None
    """
    # Create the directory if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # Save the data to CSV
    data.to_csv(save_path, index=False)
    print('Data saved successfully!')

def write_csv_file_to_aws_s3(df: pd.DataFrame, 
                             path: str, **kwargs) -> pd.DataFrame:
    """Writes an individual CSV file to AWS S3.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        path (str): The path to the CSV files on AWS S3.
        **kwargs: Additional arguments to pass to the to_csv function.
    """

    wr.s3.to_csv(df, path=path, **kwargs, index=False)
    return

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


def source_and_process_weather_data():
    """
    This function creates a point over the Bavarian Forest National Park, retrieves hourly weather data
    for the specified time period, processes the data to extract necessary weather parameters,
    and saves the processed data to a CSV file.
    """
    # Create a Point object for the Bavarian Forest National Park entry
    bavarian_forest = Point(lat=LATITUDE, lon=LONGITUDE)

    # Fetch hourly data for the location
    hourly_data = get_hourly_data(bavarian_forest)

    # Process the hourly data to extract and format necessary weather parameters
    sourced_hourly_data = process_hourly_data(hourly_data)
    
    # # Uncomment the following line to save the sourced data to a CSV file

    # # Save the processed data to a CSV file
    # save_data_to_csv(sourced_hourly_data, 'outputs/weather_data_final/weather_data_2016-24_non_imputed_forecasted.csv')

    write_csv_file_to_aws_s3(
    df=sourced_hourly_data,
    path=f"s3://{bucket}/{preprocessed_data_folder}/sourced_weather_data_2016-24_forecasted_non_imputed.csv")

    print('Sourced hourly data saved successfully to AWS S3!')

    print("Processing the sourced hourly data...")

    load_sourced_weather_data = load_csv_files_from_aws_s3(
    path=f"s3://{bucket}/{preprocessed_data_folder}/sourced_weather_data_2016-24_forecasted_non_imputed.csv",parse_dates=True)

    # Get the list of columns to process
    parameters = load_sourced_weather_data.columns.to_list()

    # Fill missing values in the weather data
    imputed_data = fill_missing_values(load_sourced_weather_data, parameters)

    return imputed_data

    # # Uncomment the following line to save the processed data to a CSV file
    # # Save the processed data to a CSV file
    # save_data_to_csv(imputed_data, 'outputs/weather_data_final/processed_weather_data_2016-24_forecasted_imputed.csv')

    """write_csv_file_to_aws_s3(
    df=imputed_data,
    path=f"s3://{bucket}/{preprocessed_data_folder}/processed_weather_data_2016-24_forecasted_imputed.csv",)"""

    #print('Processed hourly data saved successfully to AWS S3!')

