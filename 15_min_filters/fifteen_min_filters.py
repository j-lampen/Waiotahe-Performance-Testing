import pandas as pd

def filter_irradiance(fifteen_min_df, TRC=700, POA_lower_limit=450):

    # Range
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

    reasons = []

    if not WS211_ghi_lower_limit_OK:
        reasons.append("Irradiance Problem - WS211_ghi_lower_limit")

    if not WS211_ghi_upper_limit_OK:
        reasons.append("Irradiance Problem - WS211_ghi_upper_limit")

    if not WS231_ghi_lower_limit_OK:
        reasons.append("Irradiance Problem - WS231_ghi_lower_limit")

    if not WS231_ghi_upper_limit_OK:
        reasons.append("Irradiance Problem - WS231_ghi_upper_limit")

    if not WS211_poa_lower_limit_OK:
        reasons.append("Irradiance Problem - WS211_poa_lower_limit")

    if not WS231_poa_lower_limit_OK:
        reasons.append("Irradiance Problem - WS231_poa_lower_limit")

    if reasons:
        fifteen_min_df['is_valid'] = 0
        fifteen_min_df['rejection_reason'] = fifteen_min_df['rejection_reason'].apply(lambda x: x + reasons)


    # Dead value

    # Abrupt change and stability

    # Inverter status
        # Not relevant as inverters will all be unconstrained due to 3 sec filtering



    return fifteen_min_df