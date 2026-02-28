import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
import importlib

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing logic
sys.modules["streamlit"] = MagicMock()
sys.modules["yfinance"] = MagicMock()

# Implement mock_cache_data for Streamlit's st.cache_data
def mock_cache_data(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator

sys.modules["streamlit"].cache_data = mock_cache_data

# Import logic after mocking dependencies
import logic

class TestLogic(unittest.TestCase):
    def setUp(self):
        # Reload the logic module to ensure a clean state and apply mocked streamlit
        importlib.reload(logic)
        self.required_cols = ['Date', 'Tstk_Adj', 'FP1', 'FP3', 'FP6']

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_load_strategist_data_root_file(self, mock_read_csv, mock_exists):
        # Mock os.path.exists to return True for ^GSPC.csv
        def exists_side_effect(path):
            if "^GSPC.csv" in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect

        # Mock pd.read_csv to return a valid DataFrame
        mock_df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Tstk_Adj': [1.0, 1.1],
            'FP1': [100, 101],
            'FP3': [105, 106],
            'FP6': [110, 111]
        })
        mock_read_csv.return_value = mock_df

        result = logic.load_strategist_data()

        self.assertIsNotNone(result)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['Date']))
        mock_read_csv.assert_called_once()
        self.assertTrue("^GSPC.csv" in mock_read_csv.call_args[0][0])

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_load_strategist_data_fallback_file(self, mock_read_csv, mock_exists):
        # Mock os.path.exists to return False for ^GSPC.csv and True for fallback
        def exists_side_effect(path):
            if "^GSPC.csv" in path:
                return False
            if "strategist_forecast.csv" in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect

        # Mock pd.read_csv to return a valid DataFrame
        mock_df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Tstk_Adj': [1.0, 1.1],
            'FP1': [100, 101],
            'FP3': [105, 106],
            'FP6': [110, 111]
        })
        mock_read_csv.return_value = mock_df

        result = logic.load_strategist_data()

        self.assertIsNotNone(result)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['Date']))
        mock_read_csv.assert_called_once()
        self.assertTrue("strategist_forecast.csv" in mock_read_csv.call_args[0][0])

    @patch('logic.os.path.exists')
    def test_load_strategist_data_no_files(self, mock_exists):
        # Mock os.path.exists to return False for all files
        mock_exists.return_value = False

        result = logic.load_strategist_data()

        self.assertIsNone(result)

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_load_strategist_data_missing_columns(self, mock_read_csv, mock_exists):
        # Mock os.path.exists to return True for ^GSPC.csv
        mock_exists.return_value = True

        # Mock pd.read_csv to return a DataFrame missing 'FP6'
        mock_df = pd.DataFrame({
            'Date': ['2023-01-01'],
            'Tstk_Adj': [1.0],
            'FP1': [100],
            'FP3': [105]
        })
        mock_read_csv.return_value = mock_df

        result = logic.load_strategist_data()

        self.assertIsNone(result)

    @patch('logic.os.path.exists')
    @patch('logic.pd.read_csv')
    def test_load_strategist_data_exception(self, mock_read_csv, mock_exists):
        # Mock os.path.exists to return True
        mock_exists.return_value = True

        # Mock pd.read_csv to raise an Exception
        mock_read_csv.side_effect = Exception("File read error")

        result = logic.load_strategist_data()

        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
