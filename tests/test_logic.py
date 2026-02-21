import sys
import os
import unittest
import pandas as pd
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st
# Mock streamlit.cache_data decorator
def mock_cache_data(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator
mock_st.cache_data = mock_cache_data

# Mock yfinance
mock_yf = MagicMock()
sys.modules["yfinance"] = mock_yf

from logic import calc_governance

class TestLogic(unittest.TestCase):
    def test_calc_governance_error_handling(self):
        """Test calc_governance handles exceptions gracefully."""

        # Define expected error return
        expected_df = pd.DataFrame()
        expected_status = "DATA ERROR"
        expected_color = "#888888"
        expected_reason = "Feed Disconnected"

        # Test case 1: None input
        result_df, status, color, reason = calc_governance(None)
        self.assertTrue(result_df.empty)
        self.assertEqual(status, expected_status)
        self.assertEqual(color, expected_color)
        self.assertEqual(reason, expected_reason)

        # Test case 2: Empty dictionary/dataframe (missing 'Close' key)
        result_df, status, color, reason = calc_governance({})
        self.assertTrue(result_df.empty)
        self.assertEqual(status, expected_status)
        self.assertEqual(color, expected_color)
        self.assertEqual(reason, expected_reason)

        # Test case 3: DataFrame missing required columns in 'Close'
        # e.g. missing HYG
        bad_data = pd.DataFrame({'IEF': [100, 101]})
        input_data = {'Close': bad_data}
        result_df, status, color, reason = calc_governance(input_data)
        self.assertTrue(result_df.empty)
        self.assertEqual(status, expected_status)
        self.assertEqual(color, expected_color)
        self.assertEqual(reason, expected_reason)

if __name__ == '__main__':
    unittest.main()
