import unittest
import pandas as pd

import fifteen_min_filters

from helper_functions import prepare_15_min_filtering


class FilterIrradiance(unittest.TestCase):

    def setUp(self):
        # Read the CSV data from the file
        df = pd.read_csv("unit_test_data/filter_irradiance_test_data.csv", parse_dates=[0])
        print(len(df))
        self.df = prepare_15_min_filtering(df)


    def test_filter_irradiance(self):
        df = fifteen_min_filters.filter_irradiance(self.df)

        # Check if DataFrame is loaded correctly
        self.assertEqual(len(df), 120)
        # self.assertIn('Date', df.columns)
        # self.assertIn('is_valid', df.columns)
        # self.assertIn('rejection_reason', df.columns)
        #
        # # Check if active power and apparent power columns are loaded correctly
        # self.assertEqual(df.loc[0, 'VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)'], 23)
        # self.assertEqual(df.loc[1, 'VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)'], 24)
        # self.assertEqual(df.loc[2, 'VALUE(RGT-SWBD201-PQM201-S-M.UNIT1@NET1)'], 26)
        # self.assertEqual(df.loc[3, 'VALUE(RGT-SWBD201-PQM201-S-M.UNIT1@NET1)'], 27)
        #
        # # Check if is_valid and rejection_reason columns are updated correctly
        # self.assertEqual(df.loc[0, 'is_valid'], 1)
        # self.assertEqual(df.loc[1, 'is_valid'], 0)
        # self.assertEqual(df.loc[2, 'is_valid'], 1)
        # self.assertEqual(df.loc[3, 'is_valid'], 0)
        #
        # self.assertEqual(df.loc[0, 'rejection_reason'], [])
        # self.assertEqual(df.loc[1, 'rejection_reason'], ["Point of Connection Limitation"])
        # self.assertEqual(df.loc[2, 'rejection_reason'], [])
        # self.assertEqual(df.loc[3, 'rejection_reason'], ["Point of Connection Limitation"])

