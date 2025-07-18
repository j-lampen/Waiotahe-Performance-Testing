import unittest
import pandas as pd

from helper_functions import load_and_initialize_df

class TestHelperFunctions(unittest.TestCase):

    def setUp(self):
        self.filename = 'unit_test_data/load_and_initialize_df_data.csv'

    def test_load_and_initialize_df(self):
        df, inverters = load_and_initialize_df(self.filename)

        # Check if DataFrame is loaded correctly
        self.assertEqual(len(df), 3)
        self.assertIn('Date', df.columns)
        self.assertIn('is_valid', df.columns)
        self.assertIn('rejection_reason', df.columns)

        # Check if Date column is in datetime format
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['Date']))

        # Check if validation columns are initialized correctly
        self.assertTrue((df['is_valid'] == 1).all())
        self.assertTrue(df['rejection_reason'].apply(lambda x: isinstance(x, list)).all())

        # Check if inverter constraint columns are added
        for inverter in inverters:
            self.assertIn(f'is_constrained_{inverter.name}', df.columns)

        # Check if inverters are created correctly
        self.assertEqual(len(inverters), 6)
        self.assertEqual(inverters[0].label, "INV011")
        self.assertEqual(inverters[0].name, "inverter_1")

if __name__ == '__main__':
    unittest.main()