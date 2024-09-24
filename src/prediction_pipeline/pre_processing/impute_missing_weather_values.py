"""
Weather Data Visualization and Processing Script

This script visualizes temperature and precipitation data from a CSV file containing hourly weather data for the Bavarian Forest region. 
It also fills missing values in the dataset using linear interpolation and zero filling and saves the processed data to a new CSV file.

Usage:
- Ensure the data file is located at './outputs/weather_data_final/bf-weather.csv'.
- Run the script:
  $ python src/process_and_clean_weather_data.py

Output:
- The processed data is saved as 'bf-weather-imputed.csv' in the './outputs/weather_data_final/' directory.
- A plot of temperature and precipitation is saved as 'bf-weather.png' in the same directory.
"""


# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import warnings

# Ignore warnings
warnings.filterwarnings('ignore')



############################################################################################################
# Define the global variables
############################################################################################################

DATA_PATH = './outputs/weather_data_final/bf-weather.csv'
FIG_SAVE_PATH = './outputs/weather_data_final/bf-weather.png'
IMPUTED_DATA_SAVE_PATH = './outputs/weather_data_final/bf-weather-imputed.csv'


############################################################################################################
# Define the functions
############################################################################################################

def visualize_weather_data(data, fig_save_path):
    """
    Visualize temperature and precipitation data and save the plot.

    Args:
        data (pandas.DataFrame): Processed hourly weather data.
        fig_save_path (str): Path to save the generated plot.

    Returns:
        None
    """
    # Create subplots for temperature and precipitation
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))

    # Plot temperature data
    ax[0].plot(data.index, data['Temperature (°C)'], color='tab:red')
    ax[0].set_ylabel('Temperature (°C)', color='tab:red')
    ax[0].set_title('Bavarian Forest Weather Data')
    ax[0].grid(True)
    ax[0].set_xlabel('Date')

    # Plot precipitation data
    ax[1].bar(data.index, data['Precipitation (mm)'], color='tab:blue', width=4)
    ax[1].set_ylabel('Precipitation (mm)', color='tab:blue')
    ax[1].grid(True)
    ax[1].set_xlabel('Date')

    # Save the plot
    plt.tight_layout()
    plt.savefig(fig_save_path)
    plt.close()  # Close the plot to free memory

    print(f'Plot saved to {fig_save_path}')


def fill_missing_values(data, parameters):
    """
    Fill missing values in the weather data using linear interpolation or zero values.

    Args:
        data (pandas.DataFrame): Processed hourly weather data.
        parameters (list): List of column names to process.

    Returns:
        pandas.DataFrame: DataFrame with missing values filled.
    """
    total_rows = data.shape[0]

    for parameter in parameters:
        # Calculate missing values and their percentage
        missing_values = data[parameter].isnull().sum()
        missing_percentage = (missing_values / total_rows) * 100

        # Calculate zero values and their percentage
        zero_values = data[parameter].eq(0).sum()
        zero_percentage = (zero_values / total_rows) * 100

        # Check for missing values in the 'Time' column
        if parameter == 'Time' and missing_values > 0:
            print(f'Missing values in Time column: {missing_percentage:.2f}%')
            print('Please check the missing values in the Time column')
            exit()

        if missing_values == 0:
            print(f'No missing values in {parameter} column')
        else:
            print(f'Missing values in {parameter} column: {missing_percentage:.2f}%')

            if zero_percentage > 60:
                # Fill missing values with 0.0 if zero values are significant
                print(f'Zero values in {parameter} column: {zero_percentage:.2f}%')
                data[parameter].fillna(0.0, inplace=True)
                print(f'Missing values in {parameter} column filled with 0.0')
            else:
                # Use linear interpolation to fill missing values
                data[parameter].interpolate(method='linear', inplace=True)
                # Round the interpolated values to 2 decimal places
                data[parameter] = data[parameter].round(2)
                print(f'Missing values in {parameter} column filled using linear interpolation')

    return data


