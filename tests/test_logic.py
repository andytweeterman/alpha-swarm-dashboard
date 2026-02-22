import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import pandas as pd
import numpy as np

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure streamlit is mocked if not already
if "streamlit" not in sys.modules:
    mock_st = MagicMock()
    sys.modules["streamlit"] = mock_st

    def mock_cache_data(*args, **kwargs):
        # If called as decorator without parens: @st.cache_data
        if len(args) == 1 and callable(args[0]):
            return args[0]
        # If called with parens: @st.cache_data(ttl=...)
        def decorator(func):
            return func
        return decorator

    mock_st.cache_data = mock_cache_data
    mock_st.secrets = {}

# Ensure yfinance is mocked if not already, to prevent network calls during import
if "yfinance" not in sys.modules:
    sys.modules["yfinance"] = MagicMock()

# Import function from logic.py
import logic
from logic import fetch_market_data

class TestFetchMarketData(unittest.TestCase):

    def setUp(self):
        # Patch logic.yf to ensure we control the yfinance module used by logic.py
        # This handles cases where logic.py was imported by other tests with different mocks
        self.yf_patcher = patch('logic.yf')
        self.mock_yf = self.yf_patcher.start()

    def tearDown(self):
        self.yf_patcher.stop()

    def test_fetch_market_data_success(self):
        """Test successful data fetch."""
        # Create a dummy DataFrame
        dates = pd.date_range(start='2020-01-01', periods=5)
        # Create a DataFrame with some NaNs to test ffill
        data = pd.DataFrame({
            'Close': [100.0, 101.0, np.nan, 102.0, 103.0],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        }, index=dates)

        # Configure mock return value
        self.mock_yf.download.return_value = data

        # Call function
        result = fetch_market_data()

        # Verify result
        self.assertIsNotNone(result)
        # Check if ffill was applied (index 2 is nan in original, should be 101.0 in result)
        self.assertEqual(result['Close'].iloc[2], 101.0)

        # Verify yf.download called with correct tickers
        args, kwargs = self.mock_yf.download.call_args
        self.assertIn("SPY", args[0])
        self.assertIn("^DJI", args[0])

    def test_fetch_market_data_none(self):
        """Test when yf.download returns None."""
        self.mock_yf.download.return_value = None

        result = fetch_market_data()
        self.assertIsNone(result)

    def test_fetch_market_data_empty(self):
        """Test when yf.download returns empty DataFrame."""
        self.mock_yf.download.return_value = pd.DataFrame()

        result = fetch_market_data()
        self.assertIsNone(result)

    def test_fetch_market_data_exception(self):
        """Test when yf.download raises Exception."""
        self.mock_yf.download.side_effect = Exception("Network error")

        result = fetch_market_data()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
