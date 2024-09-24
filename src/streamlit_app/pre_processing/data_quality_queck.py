import pandas as pd

sensor_dict = {
    "region_1": {
        "falkenstein": {
            "in": ["Falkenstein_Parkplatz", "Falkenstein_RAUS"],
            "out": ["Falkenstein_zum_Park"],
    }},
    "region_2": {
        "lusen:": {
            "in": ["lusen_rein", "lusen_zum_Park"],
            "out": ["lusen_zum_Parkplatz"],
    }
    }
}

def convert_sensor_dictionary_to_excel_file(
        sensor_dict: dict,
        output_file_path: str) -> None:
    """
    Convert sensor dictionary to a Pandas Dataframe and save it as an Excel file.

    Args:
        sensor_dict (dict): A dictionary containing sensor data.
        output_file_path (str): The path to the output Excel file.

    Returns:
        None
    """
    regions = []
    sensor_names = []
    sensor_directions = []
    possible_sensor_ids = []

    for region, sensors in sensor_dict.items():
        for sensor_name, directions in sensors.items():
            for direction, sensor_ids in directions.items():
                regions.append(region)
                sensor_names.append(sensor_name)
                sensor_directions.append(direction)
                # Join the list into a comma-separated string
                possible_sensor_ids.append(",".join(sensor_ids))

    df = pd.DataFrame({
        "region": regions,
        "sensor_name": sensor_names,
        "sensor_direction": sensor_directions,
        "possible_sensor_ids": possible_sensor_ids
    })

    df.to_excel(output_file_path, index=False)
    
def convert_sensor_excel_file_to_dictionary(
        sensor_file_path: str) -> dict:
    """
    Convert Excel file containing sensor configuration data to a dictionary.

    Args:
        sensor_file_path (str): The path to the Excel file.

    Returns:
        dict: A dictionary containing sensor configuration.
    """
    df = pd.read_excel(sensor_file_path)
    
    sensor_dict = {}
    
    for index, row in df.iterrows():
        region = row["region"]
        sensor_name = row["sensor_name"]
        sensor_direction = row["sensor_direction"]
        possible_sensor_ids = row["possible_sensor_ids"].split(",")

        if region not in sensor_dict:
            sensor_dict[region] = {}

        if sensor_name not in sensor_dict[region]:
            sensor_dict[region][sensor_name] = {}

        if sensor_direction not in sensor_dict[region][sensor_name]:
            sensor_dict[region][sensor_name][sensor_direction] = []

        sensor_dict[region][sensor_name][sensor_direction] = possible_sensor_ids

    return sensor_dict

if __name__ == "__main__":
    convert_sensor_dictionary_to_excel_file(
        sensor_dict=sensor_dict,
        output_file_path="sensor_dictionary.xlsx")

    modified_sensor_dict = convert_sensor_excel_file_to_dictionary(
        sensor_file_path="sensor_dictionary_modified.xlsx")

    print(modified_sensor_dict)