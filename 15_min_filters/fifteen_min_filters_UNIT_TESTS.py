import unittest
import pandas as pd

import fifteen_min_filters

from helper_functions import prepare_15_min_filtering


class FilterIrradiance(unittest.TestCase):

    def test_filter_irradiance_range_ghi_good(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_ghi_good.csv")
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
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_ghi_bad_lower.csv")
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
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_ghi_bad_upper.csv")
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
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_poa_bad_lower.csv")
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
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_dead_value_bad.csv")
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
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_stability_value_good.csv")
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
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_stability_value_bad.csv")
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


