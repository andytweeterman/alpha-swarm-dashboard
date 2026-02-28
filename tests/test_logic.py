import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
import importlib

# Mock external dependencies before any imports
sys.modules['streamlit'] = MagicMock()
sys.modules['yfinance'] = MagicMock()
sys.modules['plotly'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module under test
import logic

# Implement a pass-through mock for st.cache_data to bypass caching in tests
def mock_cache_data(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator

class TestLoadStrategistData(unittest.TestCase):
    def setUp(self):
        # Override the st.cache_data decorator used in logic.py
        logic.st.cache_data = mock_cache_data

        # Reload the module to ensure the modified decorator is applied to the function
        importlib.reload(logic)

        # We also need to re-apply the mock_cache_data after reload, as reload restores original behavior
        # Wait, if we reload, logic.st will be whatever sys.modules['streamlit'] is.
        # So we should assign mock_cache_data to sys.modules['streamlit'].cache_data before reload.
        sys.modules['streamlit'].cache_data = mock_cache_data
        importlib.reload(logic)

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_root_file_exists_and_valid(self, mock_read_csv, mock_exists):
        """Test loading from the root directory when ^GSPC.csv exists and is valid."""
        # mock_exists should return True when checking for root_file, and we won't need the fallback
        mock_exists.side_effect = lambda path: "^GSPC.csv" in path

        # Create a mock DataFrame with required columns
        mock_df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Tstk_Adj': [1, 2],
            'FP1': [100, 200],
            'FP3': [100, 200],
            'FP6': [100, 200],
            'Extra': [1, 2]
        })
        mock_read_csv.return_value = mock_df

        result = logic.load_strategist_data()

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        # Verify Date column is converted to datetime
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['Date']))
        mock_read_csv.assert_called_once()
        self.assertTrue(mock_read_csv.call_args[0][0].endswith('^GSPC.csv'))

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_data_file_exists_and_valid(self, mock_read_csv, mock_exists):
        """Test loading from the data directory when root file is missing."""
        # mock_exists should return False for root file, True for fallback
        mock_exists.side_effect = lambda path: "strategist_forecast.csv" in path

        # Create a mock DataFrame with required columns
        mock_df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Tstk_Adj': [1, 2],
            'FP1': [100, 200],
            'FP3': [100, 200],
            'FP6': [100, 200]
        })
        mock_read_csv.return_value = mock_df

        result = logic.load_strategist_data()

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['Date']))
        mock_read_csv.assert_called_once()
        self.assertTrue(mock_read_csv.call_args[0][0].endswith('strategist_forecast.csv'))

    @patch('logic.os.path.exists')
    def test_no_files_exist(self, mock_exists):
        """Test behavior when neither file exists."""
        mock_exists.return_value = False

        result = logic.load_strategist_data()

        # Assertions
        self.assertIsNone(result)

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_missing_required_columns(self, mock_read_csv, mock_exists):
        """Test behavior when the file exists but lacks required columns."""
        # mock_exists returns True for the root file
        mock_exists.side_effect = lambda path: "^GSPC.csv" in path

        # Create a mock DataFrame missing 'FP6'
        mock_df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Tstk_Adj': [1, 2],
            'FP1': [100, 200],
            'FP3': [100, 200]
        })
        mock_read_csv.return_value = mock_df

        result = logic.load_strategist_data()

        # Assertions
        self.assertIsNone(result)
        mock_read_csv.assert_called_once()

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_exception_handling(self, mock_read_csv, mock_exists):
        """Test behavior when pd.read_csv raises an exception."""
        # mock_exists returns True for the root file
        mock_exists.side_effect = lambda path: "^GSPC.csv" in path

        # Make read_csv raise an Exception
        mock_read_csv.side_effect = Exception("File read error")

        result = logic.load_strategist_data()

        # Assertions
        self.assertIsNone(result)
        mock_read_csv.assert_called_once()

if __name__ == '__main__':
    unittest.main()
