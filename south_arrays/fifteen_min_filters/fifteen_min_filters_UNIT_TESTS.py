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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for GHI bad lower data.")

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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for GHI bad upper data.")

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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for POA bad lower data.")

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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for dead value on good data.")

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
        self.assertGreater(len(rejection_reasons), 0)





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

            self.assertTrue(len(rejection_reasons) > 0, "Expected at least one rejection reason for temperature range violations.")

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

            self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for dead value on bad data.")

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
            self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for abrupt change on bad data.")



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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for dead value on bad data.")

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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for abrupt change on bad data.")


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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reason for power range violation.")

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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for dead value on bad data.")

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
        self.assertGreater(len(rejection_reasons), 0, "Expected rejection reasons for abrupt change on bad data.")
