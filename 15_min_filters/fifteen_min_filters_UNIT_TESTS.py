import unittest
import pandas as pd

import fifteen_min_filters

from helper_functions import prepare_15_min_filtering


class FilterIrradiance(unittest.TestCase):

    def test_filter_irradiance_ghi_good(self):

        # Arrange
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_ghi_good.csv")  # Import data
        df['rejection_reason'] = df.apply(lambda _: [], axis=1) # Add rejection_reason col

        # Act
        df = fifteen_min_filters.filter_irradiance(df)

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('is_valid', df.columns, "'is_valid' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertTrue(all(isinstance(x, list) and len(x) == 0 for x in df['rejection_reason']), "Some rejection_reason entries are not empty lists.")
        self.assertTrue(all(df['is_valid'] == 1), "Some is_valid entries are not 1.")

    def test_filter_irradiance_ghi_bad_lower(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_ghi_bad_lower.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df = fifteen_min_filters.filter_irradiance(df)

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('is_valid', df.columns, "'is_valid' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertTrue(all(df['is_valid'] == 0), "Expected all rows to have is_valid = 0.")
        self.assertTrue(
            all(
                "Irradiance Problem - WS211_ghi_lower_limit" in reasons and
                "Irradiance Problem - WS231_ghi_lower_limit" in reasons
                for reasons in df['rejection_reason']
            ),
            "Each row should include both WS211 and WS231 GHI lower limit rejection reasons."
        )

    def test_filter_irradiance_ghi_bad_upper(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_ghi_bad_upper.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df = fifteen_min_filters.filter_irradiance(df)

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('is_valid', df.columns, "'is_valid' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertTrue(all(df['is_valid'] == 0), "Expected all rows to have is_valid = 0.")
        self.assertTrue(
            all(
                "Irradiance Problem - WS211_ghi_upper_limit" in reasons and
                "Irradiance Problem - WS231_ghi_upper_limit" in reasons
                for reasons in df['rejection_reason']
            ),
            "Each row should include both WS211 and WS231 GHI upper limit rejection reasons."
        )

    def test_filter_irradiance_poa_bad_lower(self):
        # Arrange
        df = pd.read_csv("unit_test_data/irradiance_filter_unit_test_data_poa_bad_lower.csv")
        df['rejection_reason'] = df.apply(lambda _: [], axis=1)

        # Act
        df = fifteen_min_filters.filter_irradiance(df)

        # Assert
        self.assertEqual(len(df), 15, "Expected 15 rows in DataFrame.")
        self.assertIn('15 Minute', df.columns, "'15 Minute' column missing.")
        self.assertIn('is_valid', df.columns, "'is_valid' column missing.")
        self.assertIn('rejection_reason', df.columns, "'rejection_reason' column missing.")
        self.assertTrue(all(df['is_valid'] == 0), "Expected all rows to have is_valid = 0.")
        self.assertTrue(
            all(
                "Irradiance Problem - WS211_poa_lower_limit" in reasons and
                "Irradiance Problem - WS231_poa_lower_limit" in reasons
                for reasons in df['rejection_reason']
            ),
            "Each row should include both WS211 and WS231 POA lower limit rejection reasons."
        )