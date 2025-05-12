import pandas as pd

# This file contains the 3 second filters.

def filter_ac_curtailment_periods(df):
    return None
def filter_bad_power_points(df):
    return None

def point_of_connection_constraint(df):
    # Solar farm at point of connection (POC) has a real power limit and an apparent power limit. If reaching these limits, the solar farm will be constrained.

    real_power_limit = 23.7 * 0.998  # 99.8% of 23.7 MW
    apparent_power_limit = 26.34 * 0.998  # 99.8% of 26.34 MVA

    mask_poc_limit = (
        (df['VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)'] > real_power_limit) | 
        (df['VALUE(RGT-SWBD201-PQM201-S-M.UNIT1@NET1)'] > apparent_power_limit)
    )

    df.loc[mask_poc_limit, 'is_valid'] = 0
    df.loc[mask_poc_limit, 'rejection_reason'] = df.loc[mask_poc_limit, 'rejection_reason'].apply(lambda x: x + ["Point of Connection Limitation"])

    return df

def filter_constrained_inverters(df, inverters):
    """
    Filters data based on inverter constraints.

    An inverter is constrained if its apparent power output exceeds 99.8%
    of the maximum power rating, which depends on the number of running
    modules (NRM). Each power module is rated at 1.0975 MVA.
    """
    module_rating = 1.0975  # MVA per power module
    threshold_factor = 0.998  # 99.8% threshold

    for inverter in inverters:

        # Extract SCADA column names
        apparent_power_col = inverter.apparent_power_scada_tag
        nrm_col = inverter.NRM_scada_tag
        constraint_col = f'is_constrained_{inverter.name}'

        # Compute maximum allowed apparent power per inverter
        max_allowed_power_MVA = df[nrm_col] * module_rating * threshold_factor
        max_allowed_power_KVA = max_allowed_power_MVA * 1000

        # Identify constrained inverters
        mask_constrained = df[apparent_power_col] > max_allowed_power_KVA

        # Update DataFrame for constrained inverters
        df.loc[mask_constrained, 'is_valid'] = 0
        df.loc[mask_constrained, 'rejection_reason'] = df.loc[mask_constrained, 'rejection_reason'].apply(
            lambda x: x + [f"{inverter.name} is constrained"]
        )
        df.loc[mask_constrained, constraint_col] = 1  # Mark inverter as constrained

    return df

def filter_wind_stow(df):
    """
    Identifies periods of wind stow based on wind speed sensor data.

    - Wind stow is triggered if both sensors exceed 11.11 m/s for two consecutive 3s intervals.
    - Wind stow remains active until both sensors drop below 10.55 m/s for 300s.
    """
    # Ensure "Date" column is in datetime format with seconds
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d %H:%M:%S")

    # Wind speed sensor SCADA tags
    wind_sensor_1 = 'VALUE(RGT-WSTAT211-WSWR.UNIT1@NET1)'
    wind_sensor_2 = 'VALUE(RGT-WSTAT231-WSWR.UNIT1@NET1)'

    # Thresholds
    stow_start_threshold = 11.11  # 40 km/h
    stow_end_threshold = 10.55  # 38 km/h

    # Create a new column to track wind stow
    df['is_wind_stowed'] = 0

    # Internal variables to track wind stow status
    wind_stow_active = False  # Tracks if wind stow is currently active
    consecutive_high_wind_count = 0  # Counts consecutive high-wind readings
    stow_deactivation_start = None  # Time when wind speed drops below threshold

    for i in range(len(df)):
        wind_speed_1 = df.at[i, wind_sensor_1]
        wind_speed_2 = df.at[i, wind_sensor_2]
        timestamp = pd.to_datetime(df.at[i, 'Date'])  # Ensure timestamp is datetime

        # Check if both sensors exceed the wind stow start threshold
        if wind_speed_1 > stow_start_threshold and wind_speed_2 > stow_start_threshold:
            consecutive_high_wind_count += 1
        else:
            consecutive_high_wind_count = 0  # Reset count if wind drops

        # Trigger wind stow if conditions met for two consecutive 3s readings
        if consecutive_high_wind_count >= 2 and not wind_stow_active:
            wind_stow_active = True  # Activate wind stow
            df.at[i, 'is_wind_stowed'] = 1
            stow_deactivation_start = None  # Reset release timer
            # print(f"Wind stow activated at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")  # Print full datetime

        # Check if wind stow is active
        if wind_stow_active:
            df.at[i, 'is_wind_stowed'] = 1  # Continue marking stow period

            # Check if both sensors have dropped below the release threshold
            if wind_speed_1 < stow_end_threshold and wind_speed_2 < stow_end_threshold:
                if stow_deactivation_start is None:
                    stow_deactivation_start = timestamp  # Store timestamp as datetime
                    # print(f"Wind stow deactivation started at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                elif (timestamp - stow_deactivation_start) >= pd.Timedelta(seconds=300):
                    wind_stow_active = False  # End wind stow
                    # print(f"Wind stow ended at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")  # Debugging statement
            else:
                stow_deactivation_start = None  # Reset release timer if wind picks up again

    # Apply wind stow filter
    df.loc[df['is_wind_stowed'] == 1, 'is_valid'] = 0
    df.loc[df['is_wind_stowed'] == 1, 'rejection_reason'] = df.loc[
        df['is_wind_stowed'] == 1, 'rejection_reason'].apply(
        lambda x: x + ["Wind Stow Active"]
    )

    return df