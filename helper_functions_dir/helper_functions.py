import pandas as pd
import three_sec_filters.three_sec_filters as three_sec_filters
import fifteen_min_filters.fifteen_min_filters as fifteen_min_filters

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 9)  # or 1000
pd.set_option('display.max_rows', 10)  # or 1000


# Define the Inverter class
class Inverter:
    def __init__(self, index, label):
        self.label = label  # Assign label directly
        self.name = f"inverter_{index + 1}"

        # SCADA tags
        self.active_power_scada_tag = f"VALUE(RGT-{self.label}-P.UNIT1@NET1)"
        self.apparent_power_scada_tag = f"VALUE(RGT-{self.label}-S.UNIT1@NET1)"
        self.NRM_scada_tag = f"VALUE(RGT-{self.label}-NRM.UNIT1@NET1)"

    def __repr__(self):
        return f"Inverter {self.name} ({self.label})"

def load_and_initialize_df(filename):
    df = pd.read_csv(filename, skiprows=5, dayfirst=True, parse_dates=[0])

    # Ensure "Date" column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d %H:%M:%S")

    # Initialize validation columns
    df["is_valid"] = 1
    df['rejection_reason'] = df.apply(lambda _: [], axis=1)  # Efficient list initialization

    # Define inverter labels dynamically
    inverter_labels = ["INV011", "INV012", "INV023", "INV024", "INV035", "INV036"]

    # Create inverter objects based on available labels
    inverters = [Inverter(i, label) for i, label in enumerate(inverter_labels)]

    # Add inverter constraint columns dynamically
    for inverter in inverters:
        df[f'is_constrained_{inverter.name}'] = 0

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
    print("⚙️ Applying 'Point of Connection Constraint' filter...\n")
    df_before = df["is_valid"].sum()
    df = three_sec_filters.point_of_connection_constraint(df)
    df_after = df["is_valid"].sum()
    print(f"✅ Filter applied. {df_before - df_after} rows invalidated.\n")

    # Apply Constrained Inverter Filter
    print("⚙️ Applying 'Constrained Inverter' filter...\n")
    df_before = df["is_valid"].sum()
    df = three_sec_filters.filter_constrained_inverters(df, inverters)
    df_after = df["is_valid"].sum()
    print(f"✅ Filter applied. {df_before - df_after} rows invalidated.\n")

    # Apply Wind Stow Filter
    print("⚙️ Applying 'Wind Stow' filter...\n")
    df_before = df["is_valid"].sum()
    df = three_sec_filters.filter_wind_stow(df)
    df_after = df["is_valid"].sum()
    print(f"✅ Filter applied. {df_before - df_after} rows invalidated.\n")

    # Final Count
    valid_rows = df["is_valid"].sum()
    total_rows = len(df)
    invalid_rows = total_rows - valid_rows

    print(f"📊 Final row count after 3 second filtering:")
    print(f"   ✅ Valid rows: {valid_rows}")
    print(f"   ❌ Non-valid rows: {invalid_rows}\n")

    return df  # Return fully processed DataFrame



def export_3s_data(df, valid_csv="output_data/3_sec_valid_data.csv", non_valid_csv="output_data/3_sec_non_valid_data.csv"):
    """
    Exports valid and non-valid 3-second data to separate CSV files.
    """
    # Ensure DataFrame is not empty
    if df.empty:
        print("❌ Error: Provided DataFrame is empty. No data to export.\n")
        return

    # Separate valid and non-valid data
    valid_df = df[df["is_valid"] == 1]
    non_valid_df = df[df["is_valid"] == 0]

    # Save valid data if available
    if not valid_df.empty:
        cols_to_exclude = ['is_valid', 'rejection_reason', 'is_constrained_inverter_1', 'is_constrained_inverter_2', 'is_constrained_inverter_3', 'is_constrained_inverter_4', 'is_constrained_inverter_5', 'is_constrained_inverter_6', 'is_wind_stowed']
        valid_df_to_save = valid_df.drop(columns=cols_to_exclude)
        valid_df_to_save.to_csv(valid_csv, index=False)
        print(f"✅ Valid 3-second data saved to: {valid_csv} ({len(valid_df)} rows)\n")
    else:
        print("⚠ Warning: No valid 3-second data to save. Check filtering criteria.\n")

    # Save non-valid data if available
    if not non_valid_df.empty:
        non_valid_df.to_csv(non_valid_csv, index=False)
        print(f"❌ Non-valid 3-second data saved to: {non_valid_csv} ({len(non_valid_df)} rows)\n")
    else:
        print("⚠ Warning: No non-valid 3-second data to save. Check filtering criteria.\n")



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

    print("✅ Finished 1-minute aggregation.\n")
    print(f"ℹ️ Excluded {invalid_minutes_count} 1-minute periods due to insufficient data.")

    return avg_df

def export_valid_one_minute_data(df, output_csv="one_minute_data.csv"):
    """
    Exports the aggregated 1-minute data to a CSV file.
    """
    df.to_csv(output_csv, index=False)

    print(f"✅ 1-minute averaged data saved to: {output_csv} ({len(df)} rows)\n")


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
    # Prepare one_minute_df for 15 min filtering (floor to 15 min)
    df = prepare_15_min_filtering(one_minute_df)

    # Group by 15-minute timestamp and apply filters
    filtered_dfs = []

    for time_slice, fifteen_min_df in df.groupby('15 Minute'):
        # Create a copy to avoid modifying the original
        fifteen_min_df = fifteen_min_df.copy()

        # Convert the group key (time_slice) to a pandas Timestamp (using pd.Timestamp) and then re–assign (using astype('datetime64[ns]')) so that "15 Minute" is in datetime format.
        fifteen_min_df['15 Minute'] = pd.Timestamp(time_slice)

        # Initialize rejection reasons for this time slice
        rejection_reasons = []

        # For debugging
        # print(f"time_slice: {time_slice}")
        # fifteen_min_df.to_csv("debugging/output.csv", index=False)
        # print(type(fifteen_min_df))

        # Apply all filters
        fifteen_min_df = fifteen_min_filters.filter_irradiance(fifteen_min_df, 700, 450)
        fifteen_min_df = fifteen_min_filters.filter_temperature(fifteen_min_df, rejection_reasons)
        fifteen_min_df = fifteen_min_filters.filter_wind_speed(fifteen_min_df, rejection_reasons)
        fifteen_min_df = fifteen_min_filters.filter_AC_power(fifteen_min_df, rejection_reasons)

        rejection_reasons_list = fifteen_min_df['rejection_reason'].iloc[0]
        
        # Create a new dataframe, with only one row. This row will have the mean of all the rows in the fifteen_min_df (except for the rejection_reasons column which will be the values of the first row).
        fifteen_min_df = fifteen_min_df.mean(numeric_only=True).to_frame().T
        fifteen_min_df['15 Minute'] = pd.Timestamp(time_slice)

        # Reorder columns to put '15 Minute' first
        cols = ['15 Minute'] + [col for col in fifteen_min_df.columns if col != '15 Minute']
        fifteen_min_df = fifteen_min_df[cols]

        # Add rejection reasons to the dataframe     
        fifteen_min_df['rejection_reason'] = [rejection_reasons_list]

        filtered_dfs.append(fifteen_min_df)

    # Combine all filtered DataFrames
    df = pd.concat(filtered_dfs, ignore_index=True)

    return df

def export_good_15_min_data(df, output_csv="good_15_min_data.csv"):
    """
    Exports the good 15-minute data to a CSV file.
    """

    df.to_csv(output_csv, index=False)

    print(f"✅ Good 15-minute data saved to: {output_csv} ({len(df)} rows)\n")

