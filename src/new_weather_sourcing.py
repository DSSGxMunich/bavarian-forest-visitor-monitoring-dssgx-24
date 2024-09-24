from datetime import datetime
from meteostat import Hourly, Point
import pandas as pd

LATITUDE = 49.31452390542327
LONGITUDE = 12.711573421032

# Define start and end dates for inference
#start_date = datetime.now()
#end_date = start_date + pd.Timedelta(days=7)
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 7, 22)

coco_to_coco_2_mapping = {
    1: 1,  # Clear
    2: 1,  # Fair
    3: 2,  # Cloudy
    4: 2,  # Overcast
    5: 2,  # Fog
    6: 5,  # Freezing Fog
    7: 3,  # Light Rain
    8: 3,  # Rain
    9: 3,  # Heavy Rain
    10: 5, # Freezing Rain
    11: 5, # Heavy Freezing Rain
    12: 5, # Sleet
    13: 5, # Heavy Sleet
    14: 4, # Light Snowfall
    15: 4, # Snowfall
    16: 4, # Heavy Snowfall
    17: 3, # Rain Shower
    18: 3, # Heavy Rain Shower
    19: 3, # Sleet Shower
    20: 5, # Heavy Sleet Shower
    21: 4, # Snow Shower
    22: 4, # Heavy Snow Shower
    23: 6, # Lightning
    24: 6, # Hail
    25: 6, # Thunderstorm
    26: 6, # Heavy Thunderstorm
    27: 6  # Storm
}




def get_hourly_data_forecasted(bavarian_forest):
    
    """
    Fetch hourly weather data for the Bavarian Forest - forecasted from todays date

    Returns:
        pd.DataFrame: Hourly weather data
    
    """
    data = Hourly(bavarian_forest, start_date, end_date)
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
    bavarian_forest.max_count = 10

    print(bavarian_forest.max_count)

    # Fetch hourly data for the location
    weather_hourly = get_hourly_data_forecasted(bavarian_forest)

    # Drop unnecessary columns
    weather_hourly = weather_hourly.drop(columns=['dwpt', 'wdir', 'wpgt', 'pres', 'tsun', 'prcp', 'snow'])

    # Convert the 'Time' column to datetime format
    weather_hourly['time'] = pd.to_datetime(weather_hourly['time'])
    return weather_hourly




def get_weather_data():
    
    # Source the weather data
    weather_data_df = source_weather_data()

    # Creating the new 'coco_2' column based on the mapping
    weather_data_df['coco_2'] = weather_data_df['coco'].map(coco_to_coco_2_mapping)

if __name__=="__main__":
    get_weather_data()
        