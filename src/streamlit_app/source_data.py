"""
This script files pulls the data from the Bayern Cloud API, AWS S3 bucket, and METEOSTAT API to source the data for the Bavarian Forest National Park dashboard.

The data sourced includes:
- Historic visitor counts data - from the AWS S3 bucket
- Real-time parking data - from the Bayern Cloud API
- Hourly weather data - from the METEOSTAT API

The functions in this script are used to source the data and return the dataframes for further processing.

"""
# import the necessary libraries
import pandas as pd
import awswrangler as wr
import boto3
import requests
from datetime import datetime
import os
from meteostat import Hourly, Point
from access_config_file import get_aws_credentials


########################################################################################
# AWS Setup 
########################################################################################

# Load AWS profile name 
aws_user_name = get_aws_credentials()
boto3.setup_default_session(profile_name=aws_user_name)

bucket = "dssgx-munich-2024-bavarian-forest"
raw_data_folder = "raw-data"
preprocessed_data_folder = "preprocessed_data"

########################################################################################
# Bayern Cloud setup
########################################################################################

# Load Bayern Cloud API key from environment variables
BAYERN_CLOUD_API_KEY = os.getenv('BAYERN_CLOUD_API_KEY')


# We are not using 'parkplatz-fredenbruecke-1' and 'skiwanderzentrum-zwieslerwaldhaus-2' because of inconsistency in sending data to the cloud
parking_sensors = {
     "parkplatz-graupsaege-1":["e42069a6-702f-4ef4-b3b5-04e310d97ca0",(48.92414,13.44515)],
     # "parkplatz-fredenbruecke-1":["fac08b6b-e9cb-40cd-a106-b9f2cbfc7447",()],
     "p-r-spiegelau-1": ["ee0490b2-3cc5-4adb-a527-95267257598e",(48.9178,13.35544)],
     # "skiwanderzentrum-zwieslerwaldhaus-2":[ "dd3734c2-c4fb-4e1d-a57c-9bbed8130d8f",()],
     "parkplatz-zwieslerwaldhaus-1": [ "6c9b765e-1ff9-401d-98bc-b0302ee65c62",(49.08837,13.24707)],
     # "parkplatz-zwieslerwaldhaus-nord-1": [ "4bbb3b5c-edc2-4b00-a923-91c1544aa29d",()],
     "parkplatz-nationalparkzentrum-falkenstein-2" : [ "a93b64e9-35fb-4b3e-8348-81ba8f1c0d6f",(49.06042,13.23583)],
     "scheidt-bachmann-parkplatz-1" : [ "144e1868-3051-4140-a83c-41d4b79a6d14",(48.9346,13.32418)],
     "parkplatz-nationalparkzentrum-lusen-p2" : [ "454b0f50-130b-4c21-9db2-b163e158c847",(48.8907,13.48924)],
     "parkplatz-waldhaeuser-kirche-1" : [ "454b0f50-130b-4c21-9db2-b163e158c847",(48.92842,13.4624,)],
     "parkplatz-waldhaeuser-ausblick-1" : [ "a14d8ebd-9261-49f7-875b-6a924fe34990",(48.92796,13.47076)],
     "parkplatz-skisportzentrum-finsterau-1": [ "ea474092-1064-4ae7-955e-8db099955c16",(48.94129,13.57491)],
}

########################################################################################
# Weather Data Sourcing - METEOSTAT API
########################################################################################

# Get the start time as todays date
START_TIME = datetime.now()
END_TIME = (START_TIME + pd.Timedelta(days=7))

# Coordinates of the Bavarian Forest (Haselbach)
# These coordinates are based on the weather recommendation by Google for a Bavarian Forest Weather search
LATITUDE = 49.31452390542327
LONGITUDE = 12.711573421032

########################################################################################
# Functions
########################################################################################

def source_data_from_aws_s3(path: str, **kwargs) -> pd.DataFrame:
    """Loads individual or multiple CSV files from an AWS S3 bucket.

    Args:
        path (str): The path to the CSV files on AWS S3.
        **kwargs: Additional arguments to pass to the read_csv function.

    Returns:
        pd.DataFrame: The DataFrame containing the data from the CSV files.
    """

    df = wr.s3.read_csv(path=path, **kwargs)
    return df


def source_parking_data_from_cloud(location_slug: str):
    """Sources the current occupancy data from the Bayern Cloud API.
    
    Args:
        location_slug (str): The location slug of the parking sensor.
    
    Returns:
        pd.DataFrame: A DataFrame containing the current occupancy data, occupancy rate, and capacity.
    """
    
    API_endpoint = f'https://data.bayerncloud.digital/api/v4/endpoints/list_occupancy/{location_slug}'

    request_params = {
        'token': BAYERN_CLOUD_API_KEY
    }


    response = requests.get(API_endpoint, params=request_params)
    response_json = response.json()

    # Access the first item in the @graph list
    graph_item = response_json["@graph"][0]

    # Extract the current occupancy and capacity
    current_occupancy = graph_item.get("dcls:currentOccupancy", None)
    current_capacity = graph_item.get("dcls:currentCapacity", None)
    current_occupancy_rate = graph_item.get("dcls:currentOccupancyRate", None)

    # Make a dataframe with the three values and the current time stamp in the datetime format
    parking_data = pd.DataFrame({
        "timestamp": datetime.now(), 
        "location" : [location_slug],
        "current_occupancy": [current_occupancy],
        "current_capacity": [current_capacity],
        "current_occupancy_rate": [current_occupancy_rate],
    })
    
    parking_data.reset_index(drop=True, inplace=True)

    # adding spatial information to the dataframe
    parking_df_with_spatial_info = add_spatial_info_to_parking_sensors(parking_data)

    return parking_df_with_spatial_info

def add_spatial_info_to_parking_sensors(parking_data_df):

    """
    Add spatial information to the parking data

    Args:
        parking_data_df (pd.DataFrame): DataFrame containing parking sensor data.
    
    Returns:
        pd.DataFrame: DataFrame containing parking sensor data with spatial information.
    """

    for location_slug in parking_sensors.keys():
        if location_slug in parking_data_df['location'].values:
            parking_data_df['latitude'] = parking_sensors[location_slug][1][0]
            parking_data_df['longitude'] = parking_sensors[location_slug][1][1]

            return parking_data_df

            
def merge_all_df_from_list(df_list):
    """
    Merge all the dataframes in the list into a single dataframe.

    Args:
        df_list (list): A list of pandas DataFrames to merge.

    Returns:
        pd.DataFrame: The merged DataFrame.
    """
    # Merge all the dataframes in the list with the 'time' column as index
    merged_dataframe = pd.concat(df_list, axis=0, ignore_index=True)
    return merged_dataframe


def get_hourly_data_forecasted(bavarian_forest):
    
    """
    Fetch hourly weather data for the Bavarian Forest - forecasted from todays date

    Returns:
        pd.DataFrame: Hourly weather data
    
    """
    data = Hourly(bavarian_forest, START_TIME, END_TIME)
    data = data.fetch()

    # Reset the index
    data.reset_index(inplace=True)
    return data 


def source_weather_data():

    """
    Source the weather data from METEOSTAT API

    Returns:
        pd.DataFrame: Hourly weather data for the Bavarian Forest National Park for the next 7 days
    """

    # Create a Point object for the Bavarian Forest National Park entry
    bavarian_forest = Point(lat=LATITUDE, lon=LONGITUDE)

    # Fetch hourly data for the location
    weather_hourly = get_hourly_data_forecasted(bavarian_forest)

    # Drop unnecessary columns
    weather_hourly = weather_hourly.drop(columns=['dwpt', 'snow', 'wdir', 'wpgt', 'pres', 'coco'])

    # Convert the 'Time' column to datetime format
    weather_hourly['time'] = pd.to_datetime(weather_hourly['time'])
    return weather_hourly


def source_all_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    """
    Source all the data required for the dashboard.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Historic visitor counts data, real-time parking data, and weather data.
    """
    # Load the visyor count data form AWS S3
    historic_visitor_counts = source_data_from_aws_s3(
    path=f"s3://{bucket}/{raw_data_folder}/hourly-historic-visitor-counts-all-sensors/",
    skiprows=2)

    print("Historic visitor counts data loaded successfully!")

    # Source the parking data from bayern cloud
    all_parking_dataframes = []
    for location_slug in parking_sensors.keys():
        print(f"Fetching and saving real-time occupancy data for location '{location_slug}'...")
        parking_df = source_parking_data_from_cloud(location_slug)
        all_parking_dataframes.append(parking_df)

    all_parking_data = merge_all_df_from_list(all_parking_dataframes)

    print("Parking data sourced successfully!")

    # Source the weather data
    weather_data_df = source_weather_data()

    print("Weather data sourced successfully!")

    return historic_visitor_counts, all_parking_data, weather_data_df