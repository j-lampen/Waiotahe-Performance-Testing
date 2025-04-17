import pandas as pd

def filter_irradiance(fifteen_min_df, TRC=700, POA_lower_limit=450):
    # Set up rejection reasons list
    rejection_reasons = []

    # Apply range filter
    fifteen_min_df, rejection_reasons = filter_irradiance_range(fifteen_min_df, rejection_reasons, TRC=TRC, POA_lower_limit=POA_lower_limit)

    # Apply dead value filter
    fifteen_min_df, rejection_reasons = filter_irradiance_dead_value(fifteen_min_df, rejection_reasons)

    # Apply abrupt change and stability filter
    fifteen_min_df, rejection_reasons = filter_irradiance_abrupt_change(fifteen_min_df, rejection_reasons)

    # Update flags in the DataFrame
    if rejection_reasons:
        fifteen_min_df['is_valid'] = 0
        fifteen_min_df['rejection_reason'] = fifteen_min_df['rejection_reason'].apply(lambda x: x + rejection_reasons)

    return fifteen_min_df

def filter_irradiance_range(fifteen_min_df, rejection_reasons, TRC=700, POA_lower_limit=450):

    WS211_ghi_average = fifteen_min_df['VALUE(RGT-WSTAT211-CWSAIU.UNIT1@NET1)'].mean()
    WS231_ghi_average = fifteen_min_df['VALUE(RGT-WSTAT231-CWSAIU.UNIT1@NET1)'].mean()

    WS211_poa_average = fifteen_min_df['VALUE(RGT-WSTAT211-PVAIU.UNIT1@NET1)'].mean()
    WS231_poa_average = fifteen_min_df['VALUE(RGT-WSTAT231-PVAIU.UNIT1@NET1)'].mean()

    WS211_ghi_lower_limit_OK = ((TRC * 0.5) < WS211_ghi_average)
    WS211_ghi_upper_limit_OK = (WS211_ghi_average < (TRC * 1.2))

    WS231_ghi_lower_limit_OK = ((TRC * 0.5) < WS231_ghi_average)
    WS231_ghi_upper_limit_OK = (WS231_ghi_average < (TRC * 1.2))

    WS211_poa_lower_limit_OK = (POA_lower_limit < WS211_poa_average)
    WS231_poa_lower_limit_OK = (POA_lower_limit < WS231_poa_average)

    if not WS211_ghi_lower_limit_OK:
        rejection_reasons.append("Irradiance Problem - WS211_ghi_lower_limit")

    if not WS211_ghi_upper_limit_OK:
        rejection_reasons.append("Irradiance Problem - WS211_ghi_upper_limit")

    if not WS231_ghi_lower_limit_OK:
        rejection_reasons.append("Irradiance Problem - WS231_ghi_lower_limit")

    if not WS231_ghi_upper_limit_OK:
        rejection_reasons.append("Irradiance Problem - WS231_ghi_upper_limit")

    if not WS211_poa_lower_limit_OK:
        rejection_reasons.append("Irradiance Problem - WS211_poa_lower_limit")

    if not WS231_poa_lower_limit_OK:
        rejection_reasons.append("Irradiance Problem - WS231_poa_lower_limit")

    return fifteen_min_df, rejection_reasons

def filter_irradiance_dead_value(fifteen_min_df, rejection_reasons):
    # WS211 GHI dead value check
    WS211_ghi_series = fifteen_min_df['VALUE(RGT-WSTAT211-CWSAIU.UNIT1@NET1)']  # Get full 15-min data series
    WS211_ghi_filtered = WS211_ghi_series[WS211_ghi_series > 5]  # Exclude values ≤ 5 (as per standard)
    WS211_ghi_diffs = WS211_ghi_filtered.diff().abs().dropna()  # Get absolute change between each pair of values
    WS211_ghi_stuck = len(WS211_ghi_diffs) > 0 and (WS211_ghi_diffs < 0.0001).all()  # True if all changes are < 0.0001
    if WS211_ghi_stuck:
        rejection_reasons.append("Dead value - WS211 GHI flat signal")  # Append reason if signal is considered dead

    # WS231 GHI dead value check
    WS231_ghi_series = fifteen_min_df['VALUE(RGT-WSTAT231-CWSAIU.UNIT1@NET1)']
    WS231_ghi_filtered = WS231_ghi_series[WS231_ghi_series > 5]
    WS231_ghi_diffs = WS231_ghi_filtered.diff().abs().dropna()
    WS231_ghi_stuck = len(WS231_ghi_diffs) > 0 and (WS231_ghi_diffs < 0.0001).all()
    if WS231_ghi_stuck:
        rejection_reasons.append("Dead value - WS231 GHI flat signal")

    return fifteen_min_df, rejection_reasons

def filter_irradiance_abrupt_change(fifteen_min_df, rejection_reasons):
    # WS211 GHI abrupt change check
    WS211_ghi = fifteen_min_df['VALUE(RGT-WSTAT211-CWSAIU.UNIT1@NET1)']
    WS211_ghi_avg = WS211_ghi.mean()
    WS211_ghi_std = WS211_ghi.std()
    if WS211_ghi_std > 0.05 * WS211_ghi_avg:
        rejection_reasons.append("Abrupt change - WS211 GHI standard deviation too high")

    # WS231 GHI abrupt change check
    WS231_ghi = fifteen_min_df['VALUE(RGT-WSTAT231-CWSAIU.UNIT1@NET1)']
    WS231_ghi_avg = WS231_ghi.mean()
    WS231_ghi_std = WS231_ghi.std()
    if WS231_ghi_std > 0.05 * WS231_ghi_avg:
        rejection_reasons.append("Abrupt change - WS231 GHI standard deviation too high")

    return fifteen_min_df, rejection_reasons



def filter_temperature_range(fifteen_min_df, rejection_reasons):
    lower_temp_limit = -10  # °C
    upper_temp_limit = 50   # °C

    WS211_temperature_average = fifteen_min_df['VALUE(RGT-WSTAT211-ATR.UNIT1@NET1)'].mean()
    WS231_temperature_average = fifteen_min_df['VALUE(RGT-WSTAT231-ATR.UNIT1@NET1)'].mean()

    WS211_temperature_OK = lower_temp_limit < WS211_temperature_average < upper_temp_limit
    WS231_temperature_OK = lower_temp_limit < WS231_temperature_average < upper_temp_limit

    if not WS211_temperature_OK:
        rejection_reasons.append("Temperature out of range - WS211 average outside [-10, 50] °C")

    if not WS231_temperature_OK:
        rejection_reasons.append("Temperature out of range - WS231 average outside [-10, 50] °C")

    return fifteen_min_df, rejection_reasons


def filter_temperature_dead_value(fifteen_min_df, rejection_reasons):
    # WS211 Temperature dead value check
    WS211_temp_series = fifteen_min_df['VALUE(RGT-WSTAT211-ATR.UNIT1@NET1)']  # 15-min temp data
    WS211_temp_diffs = WS211_temp_series.diff().abs().dropna()  # Absolute changes between values
    WS211_temp_stuck = len(WS211_temp_diffs) > 0 and (WS211_temp_diffs < 0.0001).all()  # True if signal is flat
    if WS211_temp_stuck:
        rejection_reasons.append("Dead value - WS211 Temperature flat signal")

    # WS231 Temperature dead value check
    WS231_temp_series = fifteen_min_df['VALUE(RGT-WSTAT231-ATR.UNIT1@NET1)']
    WS231_temp_diffs = WS231_temp_series.diff().abs().dropna()
    WS231_temp_stuck = len(WS231_temp_diffs) > 0 and (WS231_temp_diffs < 0.0001).all()
    if WS231_temp_stuck:
        rejection_reasons.append("Dead value - WS231 Temperature flat signal")

    return fifteen_min_df, rejection_reasons

def filter_temperature_abrupt_change(fifteen_min_df, rejection_reasons):
    # WS211 Temperature abrupt change check
    WS211_temp_series = fifteen_min_df['VALUE(RGT-WSTAT211-ATR.UNIT1@NET1)']
    WS211_temp_diffs = WS211_temp_series.diff().abs().dropna()  # Absolute differences between readings
    if (WS211_temp_diffs > 4).any():
        rejection_reasons.append("Abrupt change - WS211 Temperature derivative > 4")

    # WS231 Temperature abrupt change check
    WS231_temp_series = fifteen_min_df['VALUE(RGT-WSTAT231-ATR.UNIT1@NET1)']
    WS231_temp_diffs = WS231_temp_series.diff().abs().dropna()
    if (WS231_temp_diffs > 4).any():
        rejection_reasons.append("Abrupt change - WS231 Temperature derivative > 4")

    return fifteen_min_df, rejection_reasons


def filter_temperature(fifteen_min_df, rejection_reasons):
    # Set up rejection reasons list
    rejection_reasons = []

    # Apply range filter
    fifteen_min_df, rejection_reasons = filter_temperature_range(fifteen_min_df, rejection_reasons)

    # Apply dead value filter
    fifteen_min_df, rejection_reasons = filter_temperature_dead_value(fifteen_min_df, rejection_reasons)

    # Apply abrupt change and stability filter
    fifteen_min_df, rejection_reasons = filter_temperature_abrupt_change(fifteen_min_df, rejection_reasons)

    # Update flags in the DataFrame
    if rejection_reasons:
        fifteen_min_df['is_valid'] = 0
        fifteen_min_df['rejection_reason'] = fifteen_min_df['rejection_reason'].apply(lambda x: x + rejection_reasons)

    return fifteen_min_df

def filter_wind_dead_value(fifteen_min_df, rejection_reasons):
    # WS211 Wind Speed dead value check
    WS211_wind_series = fifteen_min_df['VALUE(RGT-WSTAT211-WSWR.UNIT1@NET1)']  # 15-min wind speed data
    WS211_wind_diffs = WS211_wind_series.diff().abs().dropna()  # Absolute change between readings
    WS211_wind_stuck = len(WS211_wind_diffs) > 0 and (WS211_wind_diffs < 0.0001).all()  # True if flat
    if WS211_wind_stuck:
        rejection_reasons.append("Dead value - WS211 Wind Speed flat signal")

    # WS231 Wind Speed dead value check
    WS231_wind_series = fifteen_min_df['VALUE(RGT-WSTAT231-WSWR.UNIT1@NET1)']
    WS231_wind_diffs = WS231_wind_series.diff().abs().dropna()
    WS231_wind_stuck = len(WS231_wind_diffs) > 0 and (WS231_wind_diffs < 0.0001).all()
    if WS231_wind_stuck:
        rejection_reasons.append("Dead value - WS231 Wind Speed flat signal")

    return fifteen_min_df, rejection_reasons

def filter_wind_abrupt_change(fifteen_min_df, rejection_reasons):
    # WS211 Wind Speed abrupt change check
    WS211_wind_series = fifteen_min_df['VALUE(RGT-WSTAT211-WSWR.UNIT1@NET1)']
    WS211_wind_diffs = WS211_wind_series.diff().abs().dropna()
    if (WS211_wind_diffs > 10).any():
        rejection_reasons.append("Abrupt change - WS211 Wind Speed derivative > 10")

    # WS231 Wind Speed abrupt change check
    WS231_wind_series = fifteen_min_df['VALUE(RGT-WSTAT231-WSWR.UNIT1@NET1)']
    WS231_wind_diffs = WS231_wind_series.diff().abs().dropna()
    if (WS231_wind_diffs > 10).any():
        rejection_reasons.append("Abrupt change - WS231 Wind Speed derivative > 10")

    return fifteen_min_df, rejection_reasons


def filter_wind_speed(fifteen_min_df, rejection_reasons):
    # Set up rejection reasons list
    rejection_reasons = []

    # Apply range filter
        # Wind will not be > 15 m/s due to 3 sec filtering.
        # Wind lower bound of < 0.5 m/s does not make sense.

    # Apply dead value filter
    fifteen_min_df, rejection_reasons = filter_wind_dead_value(fifteen_min_df, rejection_reasons)

    # Apply abrupt change and stability filter
    fifteen_min_df, rejection_reasons = filter_wind_abrupt_change(fifteen_min_df, rejection_reasons)

    # Update flags in the DataFrame
    if rejection_reasons:
        fifteen_min_df['is_valid'] = 0
        fifteen_min_df['rejection_reason'] = fifteen_min_df['rejection_reason'].apply(lambda x: x + rejection_reasons)

    return fifteen_min_df

def filter_power_range(fifteen_min_df, rejection_reasons, rating):
    power_series = fifteen_min_df['VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)']
    power_average = power_series.mean()

    upper_limit = 1.02 * rating
    lower_limit = -0.01 * rating

    power_OK = lower_limit <= power_average <= upper_limit

    if not power_OK:
        rejection_reasons.append("Power out of range")

    return fifteen_min_df, rejection_reasons

def filter_AC_power(fifteen_min_df, rejection_reasons):
    # Set up rejection reasons list
    rejection_reasons = []

    # Apply range filter
        # Power will not be above 1.02 * rating as is filtered out in 3 sec filters.
        # Power lower that - 0.01 * rating is interesting
    fifteen_min_df, rejection_reasons = filter_power_range(fifteen_min_df, rejection_reasons, rating=23.7)

    # # Apply dead value filter
    # fifteen_min_df, rejection_reasons =
    #
    # # Apply abrupt change and stability filter
    # fifteen_min_df, rejection_reasons =

    # Update flags in the DataFrame
    if rejection_reasons:
        fifteen_min_df['is_valid'] = 0
        fifteen_min_df['rejection_reason'] = fifteen_min_df['rejection_reason'].apply(lambda x: x + rejection_reasons)

    return fifteen_min_df