import unittest

import three_sec_filters

from helper_functions import load_and_initialize_df

class TestPointOfConnectionLimitation(unittest.TestCase):

    def setUp(self):
        # Read the CSV data from the file
        self.filename = 'unit_test_data/point_of_connection_limitation_test_data.csv'
        self.df, _ = load_and_initialize_df(self.filename)

    def test_point_of_connection_limitation(self):
        df = three_sec_filters.point_of_connection_limitation(self.df)

        # Check if DataFrame is loaded correctly
        self.assertEqual(len(df), 4) 
        self.assertIn('Date', df.columns)
        self.assertIn('is_valid', df.columns)
        self.assertIn('rejection_reason', df.columns)

        # Check if active power and apparent power columns are loaded correctly
        self.assertEqual(df.loc[0, 'VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)'], 23)
        self.assertEqual(df.loc[1, 'VALUE(RGT-SWBD201-PQM201-P-M.UNIT1@NET1)'], 24)
        self.assertEqual(df.loc[2, 'VALUE(RGT-SWBD201-PQM201-S-M.UNIT1@NET1)'], 26)
        self.assertEqual(df.loc[3, 'VALUE(RGT-SWBD201-PQM201-S-M.UNIT1@NET1)'], 27)
       

        # Check if is_valid and rejection_reason columns are updated correctly
        self.assertEqual(df.loc[0, 'is_valid'], 1)
        self.assertEqual(df.loc[1, 'is_valid'], 0)
        self.assertEqual(df.loc[2, 'is_valid'], 1)
        self.assertEqual(df.loc[3, 'is_valid'], 0)

        self.assertEqual(df.loc[0, 'rejection_reason'], [])
        self.assertEqual(df.loc[1, 'rejection_reason'], ["Point of Connection Limitation"])
        self.assertEqual(df.loc[2, 'rejection_reason'], [])
        self.assertEqual(df.loc[3, 'rejection_reason'], ["Point of Connection Limitation"])


class TestFilterConstrainedInverters(unittest.TestCase):

    def setUp(self):
        # Read the CSV data from the file
        self.filename = 'unit_test_data/filter_constrained_inverters_test_data.csv'
        self.df, self.inverters = load_and_initialize_df(self.filename)

    def test_filter_constrained_inverters(self):
        """Test filtering logic for constrained inverters."""
        df = three_sec_filters.filter_constrained_inverters(self.df, self.inverters)
        print(df.to_string())
        # Check if DataFrame is loaded correctly
        self.assertEqual(len(df), 8)
        self.assertIn('Date', df.columns)
        self.assertIn('is_valid', df.columns)
        self.assertIn('rejection_reason', df.columns)

        # Given

        # Check if NRM is correct
        self.assertEqual(df.loc[0, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 1)
        self.assertEqual(df.loc[1, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 1)
        self.assertEqual(df.loc[2, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 2)
        self.assertEqual(df.loc[3, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 2)
        self.assertEqual(df.loc[4, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 3)
        self.assertEqual(df.loc[5, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 3)
        self.assertEqual(df.loc[6, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 4)
        self.assertEqual(df.loc[7, 'VALUE(RGT-INV011-NRM.UNIT1@NET1)'], 4)

        # Check if apparent power columns are loaded correctly. S
        self.assertEqual(df.loc[0, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 995.305)
        self.assertEqual(df.loc[1, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 1195.305)
        self.assertEqual(df.loc[2, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 2090.61)
        self.assertEqual(df.loc[3, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 2290.61)
        self.assertEqual(df.loc[4, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 3185.915)
        self.assertEqual(df.loc[5, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 3385.915)
        self.assertEqual(df.loc[6, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 4281.22)
        self.assertEqual(df.loc[7, 'VALUE(RGT-INV011-S.UNIT1@NET1)'], 4481.22)

        # When


        # Then
        self.assertEqual(df.loc[0, 'is_valid'], 1)
        self.assertEqual(df.loc[1, 'is_valid'], 0)
        self.assertEqual(df.loc[1, 'rejection_reason'], ["inverter_1 is constrained"])

        # self.assertEqual(df.loc[2, 'is_valid'], 1)
        # self.assertEqual(df.loc[3, 'is_valid'], 0)
        #
        # self.assertEqual(df.loc[4, 'is_valid'], 1)
        # self.assertEqual(df.loc[5, 'is_valid'], 0)
        #
        # self.assertEqual(df.loc[6, 'is_valid'], 1)
        # self.assertEqual(df.loc[7, 'is_valid'], 0)

if __name__ == '__main__':
    unittest.main()