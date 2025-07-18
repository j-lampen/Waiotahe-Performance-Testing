import pandas as pd
import three_sec_filters.three_sec_filters as three_sec_filters
import fifteen_min_filters.fifteen_min_filters as fifteen_min_filters

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 9)  # or 1000
pd.set_option('display.max_rows', 10)  # or 1000


# Define the Inverter class
class Inverter:
    def __init__(self, inverter_number, label):
        self.label = label  # Assign label directly
        self.name = f"inverter_{inverter_number}"

        # SCADA tags
        self.active_power_scada_tag = f"VALUE(\HTR-{self.label}-P.UNIT3@NET2\)" # Example: VALUE(\HTR-INV048-P.UNIT3@NET2\)
        self.apparent_power_scada_tag = f"VALUE(\HTR-{self.label}-S.UNIT3@NET2\)"
        self.NRM_scada_tag = f"VALUE(\HTR-{self.label}-NRM.UNIT3@NET2\)"

    def __repr__(self):
        return f"Inverter {self.name} ({self.label})"

def load_and_initialize_df(filename):
    """
    Loads and initializes a DataFrame from a CSV file.
    """

    # Visual break
    print("-" * 60)

    print(f"\n🔹 Loading data from: {filename}\n")
    df = pd.read_csv(filename, skiprows=5, parse_dates=[0], date_format="%d/%m/%Y %I:%M:%S %p")

    print(df.head(5))

    print(f"🔹 Loaded {len(df)} rows successfully.\n")


    # Initialize validation columns
    df["is_valid"] = 1
    df['rejection_reason'] = df.apply(lambda _: [], axis=1)  # Efficient list initialization

    # Define inverter labels 
    inverter_labels = ["INV024", "INV035", "INV036", "INV047", "INV048"]

    # Create inverter objects based on available labels

    inverters = [Inverter(int(label[5]), label) for i, label in enumerate(inverter_labels)]

    # Add inverter constraint columns dynamically
    for inverter in inverters:
        df[f'is_constrained_{inverter.name}'] = 0

    # Visual break
    print("-" * 60)

    return df, inverters  # Return DataFrame and inverter list

def apply_three_second_filters(df, inverters):
    """
    Applies multiple filters in sequence to the same DataFrame.
    - Ensures each filter modifies df and passes it along.
    - Splits the valid and non-valid data and saves them into separate CSV files.
    - Prints information about each filtering step.
    """

    print("\n🔹 Starting 3-second filtering process...\n")


    # Apply Point of Connection Limitation Filter
    print("    ⚙️  Applying 'Point of Connection Constraint' filter...\n")
    df_before = df["is_valid"].sum()
    df = three_sec_filters.point_of_connection_constraint(df)
    df_after = df["is_valid"].sum()
    print(f"    ✅  Filter applied. {df_before - df_after} rows invalidated.\n")

    # Apply Constrained Inverter Filter
    print("     ⚙️  Applying 'Constrained Inverter' filter...\n")
    df_before = df["is_valid"].sum()
    df = three_sec_filters.filter_constrained_inverters(df, inverters)
    df_after = df["is_valid"].sum()
    print(f"    ✅  Filter applied. {df_before - df_after} rows invalidated.\n")

    # Apply Wind Stow Filter
    print("     ⚙️  Applying 'Wind Stow' filter...\n")
    df_before = df["is_valid"].sum()
    df = three_sec_filters.filter_wind_stow(df)
    df_after = df["is_valid"].sum()
    print(f"    ✅ Filter applied. {df_before - df_after} rows invalidated.\n")

    # Check if there are enough points in each minute
    print("     ⚙️  Checking if there are enough points in each minute...\n")
    df_before = df["is_valid"].sum()
    df = three_sec_filters.check_enough_points_in_minute(df)
    df_after = df["is_valid"].sum()
    print(f"    ✅ Filter applied. {df_before - df_after} rows invalidated.\n")

    # Final Count
    valid_rows = df["is_valid"].sum()
    total_rows = len(df)
    invalid_rows = total_rows - valid_rows

    return df  # Return fully processed DataFrame



def export_3s_data(df, filename="output_data/3_sec_data.csv"):
    """
    Exports 3-second data to a CSV file.
    """
    # Ensure DataFrame is not empty
    if df.empty:
        print("❌ Error: Provided DataFrame is empty. No data to export.\n")
        return
    cols_to_exclude = ['is_constrained_inverter_4', 'is_constrained_inverter_5', 'is_constrained_inverter_6', 'is_constrained_inverter_7', 'is_constrained_inverter_8', 'is_wind_stowed']
    df_to_save = df.drop(columns=cols_to_exclude)
    df_to_save.to_csv(filename, index=False)
    print(f"🔹 3-second data saved to: {filename} ({len(df)} rows)\n")
  
    # Visual break
    print("-" * 60)



def aggregate_to_one_minute(df):
    """
    Aggregates the filtered 3-second data into 1-minute averages.
    - Excludes 1-minute periods that have fewer than 5 valid 3-second data points.
    """
    print("\n🔹 Starting 1-minute aggregation...\n")

    # Make a copy to avoid modifying the original DataFrame
    df = df.copy()

    # Ensure "Date" column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Round timestamp to the nearest minute
    df['Minute'] = df['Date'].dt.floor('min')

    # Count valid points per minute
    valid_counts = df.groupby('Minute').size().reset_index(name='valid_count')

    # Identify valid and invalid minutes
    valid_minutes = valid_counts[valid_counts['valid_count'] >= 5]['Minute']
    invalid_minutes_count = (valid_counts['valid_count'] < 5).sum()

    # Filter original valid data to include only these valid minutes
    df_filtered = df[df['Minute'].isin(valid_minutes)]

    # Ensure only numeric columns are averaged
    numeric_cols = df_filtered.select_dtypes(include=['number']).columns
    avg_df = df_filtered.groupby('Minute')[numeric_cols].mean().reset_index()

    print(f"🔹  Finished 1-minute aggregation.\n")
    print(f"🔹 Excluded {invalid_minutes_count} 1-minute periods due to insufficient data.\n")

    return avg_df

def export_valid_one_minute_data(df, output_csv="one_minute_data.csv"):
    """
    Exports the aggregated 1-minute data to a CSV file.
    """
    df.to_csv(output_csv, index=False)

    print(f"🔹  1-minute averaged data saved to: {output_csv} ({len(df)} rows)\n")

    # Visual break
    print("-" * 60)


def prepare_15_min_filtering(df):
    # Rename the first column
    original_col = df.columns[0]
    df = df.rename(columns={original_col: '15 Minute'})

    # Convert to datetime and floor to 15-minute, ensuring the entire column is in datetime64[ns] format
    df['15 Minute'] = pd.to_datetime(df['15 Minute'], format="%Y-%m-%d %H:%M:%S").dt.floor('15min').astype('datetime64[ns]')

    # Add "is_valid" columnS
    df["is_valid"] = 1
    df['rejection_reason'] = df.apply(lambda _: [], axis=1)

    return df

def apply_15_min_filter(one_minute_df):
    """
    Applies 15-minute filters to the DataFrame.
    Filters include:
    - Irradiance (range, dead value, abrupt change)
    - Temperature (range, dead value, abrupt change)
    - Wind Speed (dead value, abrupt change)
    - Power (range, dead value, abrupt change)
    
    Note: If any filter fails, the entire 15-minute slice is marked as invalid.

    Input:
    - df: DataFrame with 1 minute data

    Output:
    - df: DataFrame with 15-minute data marked as valid or invalid with rejection reasons

    """

    print("\n🔹 Starting 15-minute filtering process...\n")
    # Prepare one_minute_df for 15 min filtering (floor to 15 min)
    df = prepare_15_min_filtering(one_minute_df)

    # Group by 15-minute timestamp and apply filters
    filtered_dfs = []

    for time_slice, fifteen_min_group in df.groupby('15 Minute'):

        # Check that there are 15 rows in the fifteen_min_group
        if len(fifteen_min_group) != 15:
            enough_data = False
        else:
            enough_data = True

        # fifteen_min_group is a DataFrame with 15, one minute data points for a single 15 minute period
        fifteen_min_group = fifteen_min_group.copy()

        # Convert the group key (time_slice) to a pandas Timestamp (using pd.Timestamp) 
        fifteen_min_group['15 Minute'] = pd.Timestamp(time_slice)

        # Apply all filters
        fifteen_min_group = fifteen_min_filters.filter_irradiance(fifteen_min_group, 400, 250)
        fifteen_min_group = fifteen_min_filters.filter_temperature(fifteen_min_group)
        fifteen_min_group = fifteen_min_filters.filter_wind_speed(fifteen_min_group)
        fifteen_min_group = fifteen_min_filters.filter_AC_power(fifteen_min_group)

        rejection_reasons_list = fifteen_min_group['rejection_reason'].iloc[0]
        
        # Create a new dataframe, with only one row. This row will have the mean of all the rows in the fifteen_min_df 
        fifteen_min_df = fifteen_min_group.mean(numeric_only=True).to_frame().T
        fifteen_min_df['15 Minute'] = pd.Timestamp(time_slice)

        # Reorder columns to put '15 Minute' first
        cols = ['15 Minute'] + [col for col in fifteen_min_df.columns if col != '15 Minute']
        fifteen_min_df = fifteen_min_df[cols]

        # Add rejection reasons to the dataframe     
        fifteen_min_df['rejection_reason'] = [rejection_reasons_list]

        if not enough_data:
            fifteen_min_df['is_valid'] = 0
            fifteen_min_df['rejection_reason'] = fifteen_min_df['rejection_reason'].apply(lambda x: x + ["Not enough 1 minute data in 15 minute period"])  

        filtered_dfs.append(fifteen_min_df)

    # Combine all filtered DataFrames
    df = pd.concat(filtered_dfs, ignore_index=True)

    print(f"🔹  Finished 15-minute filtering process.\n")

    return df

def export_good_15_min_data(df):
    """
    Exports the good 15-minute data to a good_15_min_data.csv file only if is_valid is 1    
    """
    # good
    good_15_min_df = df[df['is_valid'] == 1]
    good_15_min_df.to_csv("output_data/good_15_min_data.csv", index=False)

    print(f"🔹 Good 15-minute data saved to: output_data/good_15_min_data.csv ({len(good_15_min_df)} rows)\n")

    # bad
    bad_15_min_df = df[df['is_valid'] == 0]
    bad_15_min_df.to_csv("output_data/bad_15_min_data.csv", index=False)

    print(f"🔹 Bad 15-minute data saved to: output_data/bad_15_min_data.csv ({len(bad_15_min_df)} rows)\n")





