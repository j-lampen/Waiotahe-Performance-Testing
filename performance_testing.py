import helper_functions_dir.helper_functions as helper_functions
import pandas as pd


def main():

    # # Import data
    # raw_df, inverters = helper_functions.load_and_initialize_df(
    #     "input_data/Edgecumbe Raw Sensor Data (14 days, 3s intervals).csv")  # Load raw data
    # # print(raw_df)

    # # Apply 3-second filters
    # filtered_df_3s = helper_functions.apply_three_second_filters(raw_df, inverters) # Apply filter
    # helper_functions.export_3s_data(filtered_df_3s) # Export data
    # # print(filtered_df_3s)

    # # Average to 1 minute
    # filtered_df_3s = pd.read_csv("output_data/3_sec_valid_data.csv") # Import data
    # one_minute_df = helper_functions.aggregate_to_one_minute(filtered_df_3s) # Average
    # helper_functions.export_valid_one_minute_data(one_minute_df, "output_data/one_minute_data.csv")  # Export data
    # # print(one_minute_df)

    # Filter and Average to 15 mins
    one_minute_df = pd.read_csv("output_data/one_minute_data.csv") # Import data
    fifteen_min_df = helper_functions.apply_15_min_filter(one_minute_df)

    # # Export data
    # fifteen_min_df.to_csv("output_data/fifteen_min_data.csv", index=False)


main()

