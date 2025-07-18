import helper_functions_dir.helper_functions as helper_functions
import pandas as pd

# Ensure all columns are printed (disable column truncation)
pd.set_option('display.max_columns', None)


def main():

    # Import data
    raw_df, inverters = helper_functions.load_and_initialize_df(
        "input_data/waiotahe_north_raw_sensor_data.csv")  # Load raw data

    # Apply 3-second filters
    filtered_df_3s = helper_functions.apply_three_second_filters(raw_df, inverters) # Apply filter
    helper_functions.export_3s_data(filtered_df_3s) # Export data

    # Average to 1 minute
    filtered_df_3s = pd.read_csv("output_data/3_sec_data.csv") # Import data
    filtered_df_3s = filtered_df_3s[filtered_df_3s["is_valid"] == 1] # Only keep valid data
    one_minute_df = helper_functions.aggregate_to_one_minute(filtered_df_3s) # Average
    helper_functions.export_valid_one_minute_data(one_minute_df, "output_data/one_minute_data.csv")  # Export data

    # Filter and Average to 15 mins
    one_minute_df = pd.read_csv("output_data/one_minute_data.csv") # Import data
    fifteen_min_df = helper_functions.apply_15_min_filter(one_minute_df)
    helper_functions.export_good_15_min_data(fifteen_min_df)
    

main()

