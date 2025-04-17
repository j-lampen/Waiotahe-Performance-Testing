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