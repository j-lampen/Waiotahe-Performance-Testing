import unittest
import pandas as pd

import fifteen_min_filters


class FilterIrradiance(unittest.TestCase):

    def test_filter_irradiance_range_ghi_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance/irradiance_filter_unit_test_data_ghi_good.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_irradiance_range(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for GHI good data.")

    def test_filter_irradiance_range_ghi_bad_lower(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance/irradiance_filter_unit_test_data_ghi_bad_lower.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_irradiance_range(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Irradiance Problem - WS211_ghi_lower_limit", rejection_reasons)
        self.assertIn("Irradiance Problem - WS231_ghi_lower_limit", rejection_reasons)

    def test_filter_irradiance_range_ghi_bad_upper(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance/irradiance_filter_unit_test_data_ghi_bad_upper.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_irradiance_range(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Irradiance Problem - WS211_ghi_upper_limit", rejection_reasons)
        self.assertIn("Irradiance Problem - WS231_ghi_upper_limit", rejection_reasons)

    def test_filter_irradiance_range_poa_bad_lower(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance/irradiance_filter_unit_test_data_poa_bad_lower.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_irradiance_range(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Irradiance Problem - WS211_poa_lower_limit", rejection_reasons)
        self.assertIn("Irradiance Problem - WS231_poa_lower_limit", rejection_reasons)

    def test_filter_irradiance_dead_value_bad(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance/irradiance_filter_unit_test_data_dead_value_bad.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_irradiance_dead_value(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")

        self.assertIn("Dead value - WS211 GHI flat signal", rejection_reasons)
        self.assertIn("Dead value - WS231 GHI flat signal", rejection_reasons)

    def test_filter_irradiance_stability_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance/irradiance_filter_unit_test_data_stability_value_good.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Sanity check on test input (optional but recommended)
        ghi = df['VALUE(RGT-WSTAT211-CWSAIU.UNIT1@NET1)']
        mean_val = ghi.mean()
        std_val = ghi.std()
        self.assertLessEqual(std_val, 0.05 * mean_val,
                             f"Test CSV may be misconfigured: std ({std_val:.4f}) > 5% of mean ({mean_val:.4f})")

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_irradiance_abrupt_change(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for stable irradiance data.")

    def test_filter_irradiance_stability_bad(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance/irradiance_filter_unit_test_data_stability_value_bad.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Sanity check: confirm WS211 and WS231 GHI are both unstable
        WS211 = df['VALUE(RGT-WSTAT211-CWSAIU.UNIT1@NET1)']
        WS231 = df['VALUE(RGT-WSTAT231-CWSAIU.UNIT1@NET1)']
        WS211_mean, WS211_std = WS211.mean(), WS211.std()
        WS231_mean, WS231_std = WS231.mean(), WS231.std()

        self.assertGreater(WS211_std, 0.05 * WS211_mean,
                           f"WS211 GHI is too stable: std ({WS211_std:.4f}) ≤ 5% of mean ({WS211_mean:.4f})")
        self.assertGreater(WS231_std, 0.05 * WS231_mean,
                           f"WS231 GHI is too stable: std ({WS231_std:.4f}) ≤ 5% of mean ({WS231_mean:.4f})")

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_irradiance_abrupt_change(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Abrupt change - WS211 GHI standard deviation too high", rejection_reasons,
                      "Expected WS211 GHI to be flagged for instability.")
        self.assertIn("Abrupt change - WS231 GHI standard deviation too high", rejection_reasons,
                      "Expected WS231 GHI to be flagged for instability.")





class FilterTemperature(unittest.TestCase):

        def test_filter_temperature_range_good(self):
            # Arrange
            df = pd.read_csv("unit_test_data/temperature/temperature_filter_unit_test_data_range_good.csv")
            df['rejection_reason'] = df.apply(lambda _: [], axis=1)

            # Act
            df, rejection_reasons = fifteen_min_filters.filter_temperature_range(df, rejection_reasons=[])

            # Assert
            self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
            self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
            self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
            self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for temperature good data.")

        def test_filter_temperature_range_bad(self):
            # Arrange
            df = pd.read_csv("unit_test_data/temperature/temperature_filter_unit_test_data_range_bad.csv")
            df['rejection_reason'] = df.apply(lambda _: [], axis=1)

            # Act
            df, rejection_reasons = fifteen_min_filters.filter_temperature_range(df, rejection_reasons=[])

            # Assert
            self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
            self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
            self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")

            self.assertTrue(len(rejection_reasons) > 0,
                            "Expected at least one rejection reason for temperature range violations.")
            self.assertIn("Temperature out of range - WS211 average outside [-10, 50] °C", rejection_reasons)
            self.assertIn("Temperature out of range - WS231 average outside [-10, 50] °C", rejection_reasons)

        def test_filter_temperature_dead_value_good(self):
            # Arrange
            df = pd.read_csv("unit_test_data/temperature/temperature_filter_unit_test_data_dead_value_good.csv")
            df['rejection_reason'] = df.apply(lambda _: [], axis=1)

            # Act
            df, rejection_reasons = fifteen_min_filters.filter_temperature_dead_value(df, rejection_reasons=[])

            # Assert
            self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
            self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
            self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
            self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for dead value on good data.")

        def test_filter_temperature_dead_value_bad(self):
            # Arrange
            df = pd.read_csv("unit_test_data/temperature/temperature_filter_unit_test_data_dead_value_bad.csv")
            df['rejection_reason'] = df.apply(lambda _: [], axis=1)

            # Act
            df, rejection_reasons = fifteen_min_filters.filter_temperature_dead_value(df, rejection_reasons=[])

            # Assert
            self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
            self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
            self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")

            self.assertIn("Dead value - WS211 Temperature flat signal", rejection_reasons,
                          "Expected WS211 Temperature to be flagged as a dead value.")
            self.assertIn("Dead value - WS231 Temperature flat signal", rejection_reasons,
                          "Expected WS231 Temperature to be flagged as a dead value.")

        def test_filter_temperature_abrupt_change_good(self):
            # Arrange
            df = pd.read_csv("unit_test_data/temperature/temperature_filter_unit_test_data_abrupt_change_good.csv")
            df['rejection_reason'] = df.apply(lambda _: [], axis=1)

            # Act
            df, rejection_reasons = fifteen_min_filters.filter_temperature_abrupt_change(df, rejection_reasons=[])

            # Assert
            self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
            self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
            self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
            self.assertEqual(len(rejection_reasons), 0,
                             "Expected no rejection reasons for temperature abrupt change (good data).")

        def test_filter_temperature_abrupt_change_bad(self):
            # Arrange
            df = pd.read_csv("unit_test_data/temperature/temperature_filter_unit_test_data_abrupt_change_bad.csv")
            df['rejection_reason'] = df.apply(lambda _: [], axis=1)

            # Act
            df, rejection_reasons = fifteen_min_filters.filter_temperature_abrupt_change(df, rejection_reasons=[])

            # Assert
            self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
            self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
            self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
            self.assertIn("Abrupt change - WS211 Temperature derivative > 4", rejection_reasons,
                          "Expected WS211 Temperature to be flagged for abrupt change.")
            self.assertIn("Abrupt change - WS231 Temperature derivative > 4", rejection_reasons,
                          "Expected WS231 Temperature to be flagged for abrupt change.")



class FilterWind(unittest.TestCase):

    def test_filter_wind_dead_value_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/wind/wind_filter_unit_test_data_dead_value_good.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_wind_dead_value(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for wind dead value (good data).")

    def test_filter_wind_dead_value_bad(self):
        # Arrange
        df = pd.read_csv("unit_test_data/wind/wind_filter_unit_test_data_dead_value_bad.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_wind_dead_value(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Dead value - WS211 Wind Speed flat signal", rejection_reasons,
                      "Expected WS211 Wind Speed to be flagged as a dead value.")
        self.assertIn("Dead value - WS231 Wind Speed flat signal", rejection_reasons,
                      "Expected WS231 Wind Speed to be flagged as a dead value.")

    def test_filter_wind_abrupt_change_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/wind/wind_filter_unit_test_data_abrupt_change_good.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_wind_abrupt_change(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for wind abrupt change (good data).")

    def test_filter_wind_abrupt_change_bad(self):
        # Arrange
        df = pd.read_csv("unit_test_data/wind/wind_filter_unit_test_data_abrupt_change_bad.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_wind_abrupt_change(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Abrupt change - WS211 Wind Speed derivative > 10", rejection_reasons,
                      "Expected WS211 Wind Speed to be flagged for abrupt change.")
        self.assertIn("Abrupt change - WS231 Wind Speed derivative > 10", rejection_reasons,
                      "Expected WS231 Wind Speed to be flagged for abrupt change.")


class FilterPower(unittest.TestCase):

    def test_filter_power_range_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/power/power_filter_unit_test_data_range_good.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)
        rating = 23.7 # MW

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_power_range(df, rejection_reasons=[], rating=rating)

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for power range (good data).")

    def test_filter_power_range_bad(self):
        # Arrange
        df = pd.read_csv("unit_test_data/power/power_filter_unit_test_data_range_bad.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)
        rating = 23.7 # MW

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_power_range(df, rejection_reasons=[], rating=rating)

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Power out of range", rejection_reasons,
                      "Expected rejection reason for power range violation.")

    def test_filter_power_dead_value_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/power/power_filter_unit_test_data_dead_value_good.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_power_dead_value(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for power dead value (good data).")

    def test_filter_power_dead_value_bad(self):
        # Arrange
        df = pd.read_csv("unit_test_data/power/power_filter_unit_test_data_dead_value_bad.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_power_dead_value(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Dead value - Power flat signal (< 0.1% change in 3 readings)", rejection_reasons,
                      "Expected power to be flagged as a dead value.")

    def test_filter_power_abrupt_change_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/power/power_filter_unit_test_data_abrupt_change_good.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Sanity check on test input
        power = df['VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)']
        mean_val = power.mean()
        std_val = power.std()
        self.assertLessEqual(std_val, 0.05 * mean_val,
                           f"Test CSV may be misconfigured: std ({std_val:.4f}) > 5% of mean ({mean_val:.4f})")

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_power_abrupt_change(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertEqual(len(rejection_reasons), 0, "Expected no rejection reasons for stable power data.")

    def test_filter_power_abrupt_change_bad(self):
        # Arrange
        df = pd.read_csv("unit_test_data/power/power_filter_unit_test_data_abrupt_change_bad.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Sanity check: confirm power is unstable
        power = df['VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)']
        mean_val = power.mean()
        std_val = power.std()
        self.assertGreater(std_val, 0.05 * mean_val,
                         f"Test CSV may be misconfigured: std ({std_val:.4f}) ≤ 5% of mean ({mean_val:.4f})")

        # Act
        df, rejection_reasons = fifteen_min_filters.filter_power_abrupt_change(df, rejection_reasons=[])

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertIn("Abrupt change - Power standard deviation too high (> 5% of average)", rejection_reasons,
                      "Expected power to be flagged for instability.")
