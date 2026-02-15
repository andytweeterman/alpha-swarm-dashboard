import sys
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import datetime
import os

# Mock pandas_datareader before importing the module under test
# This is necessary because the module imports pandas_datareader at the top level
mock_pdr = MagicMock()
mock_data = MagicMock()
mock_pdr.data = mock_data
sys.modules["pandas_datareader"] = mock_pdr
sys.modules["pandas_datareader.data"] = mock_data

# Add repo root to path to import research.employment_data_prep
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.employment_data_prep import fetch_employment_data

class TestEmploymentData(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test
        mock_data.reset_mock()
        mock_data.DataReader.side_effect = None
        mock_data.DataReader.return_value = None

    def test_fetch_employment_data_success(self):
        # Setup mock return value
        mock_df = pd.DataFrame({
            'PAYEMS': [1, 2],
            'UNRATE': [3, 4],
            'ICSA': [5, 6]
        })
        mock_data.DataReader.return_value = mock_df

        # Call function
        df = fetch_employment_data()

        # Assertions
        self.assertIsNotNone(df)
        pd.testing.assert_frame_equal(df, mock_df)
        mock_data.DataReader.assert_called_once()

        # Check arguments
        args, _ = mock_data.DataReader.call_args
        self.assertEqual(args[0], ['PAYEMS', 'UNRATE', 'ICSA'])
        self.assertEqual(args[1], 'fred')
        self.assertIsInstance(args[2], datetime.datetime) # start date
        self.assertIsInstance(args[3], datetime.datetime) # end date

    def test_fetch_employment_data_missing_columns(self):
        # Setup mock with missing columns (simulating partial data or warning scenario)
        mock_df = pd.DataFrame({
            'PAYEMS': [1, 2],
            # Missing UNRATE and ICSA
        })
        mock_data.DataReader.return_value = mock_df

        # Call function
        df = fetch_employment_data()

        # Assertions
        self.assertIsNotNone(df)
        # Verify it returns the dataframe even if columns are missing
        pd.testing.assert_frame_equal(df, mock_df)

    def test_fetch_employment_data_failure(self):
        # Setup mock to raise exception
        mock_data.DataReader.side_effect = Exception("API Error")

        # Call function
        df = fetch_employment_data()

        # Assertions
        self.assertIsNone(df)

if __name__ == '__main__':
    unittest.main()
