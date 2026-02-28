import unittest
import sys
import os
import importlib
from unittest.mock import MagicMock, patch

# Add the src/ or root directory to the path so we can import logic.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to mock pandas, numpy, yfinance, plotly, and streamlit
# because tests might run in environments where they are not installed.
mock_pd = MagicMock()
mock_np = MagicMock()
mock_yf = MagicMock()
mock_plotly = MagicMock()
mock_plotly_go = MagicMock()
mock_st = MagicMock()

# Define the pass-through decorator for st.cache_data
def mock_cache_data(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator

mock_st.cache_data = mock_cache_data

# Patch sys.modules before importing the logic module
sys.modules['pandas'] = mock_pd
sys.modules['numpy'] = mock_np
sys.modules['yfinance'] = mock_yf
sys.modules['plotly'] = mock_plotly
sys.modules['plotly.graph_objects'] = mock_plotly_go
sys.modules['streamlit'] = mock_st

import logic

class TestFetchMarketData(unittest.TestCase):
    def setUp(self):
        # Reload logic to ensure it picks up the mocks from sys.modules
        importlib.reload(logic)

        # Reset the mock for yf.download to a clean state for each test
        self.mock_yf_download = MagicMock()
        logic.yf.download = self.mock_yf_download

    def test_fetch_market_data_success(self):
        """Test successful fetch and forward-fill of market data."""
        # Create a mock DataFrame that behaves like pandas DataFrame
        mock_data = MagicMock()
        mock_data.empty = False

        # Create a mock for ffill() that returns a new mock object or the same
        mock_ffilled_data = MagicMock()
        mock_data.ffill.return_value = mock_ffilled_data

        self.mock_yf_download.return_value = mock_data

        result = logic.fetch_market_data()

        self.mock_yf_download.assert_called_once()
        mock_data.ffill.assert_called_once()
        self.assertEqual(result, mock_ffilled_data)

    def test_fetch_market_data_none(self):
        """Test fetch_market_data when yf.download returns None."""
        self.mock_yf_download.return_value = None

        result = logic.fetch_market_data()

        self.mock_yf_download.assert_called_once()
        self.assertIsNone(result)

    def test_fetch_market_data_empty(self):
        """Test fetch_market_data when yf.download returns an empty DataFrame."""
        mock_data = MagicMock()
        mock_data.empty = True
        self.mock_yf_download.return_value = mock_data

        result = logic.fetch_market_data()

        self.mock_yf_download.assert_called_once()
        self.assertIsNone(result)

    def test_fetch_market_data_exception(self):
        """Test fetch_market_data when yf.download raises an exception."""
        self.mock_yf_download.side_effect = Exception("Network Error")

        result = logic.fetch_market_data()

        self.mock_yf_download.assert_called_once()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()