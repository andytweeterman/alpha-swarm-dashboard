
import sys
import os
import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import numpy as np

# Mock dependencies
sys.modules["streamlit"] = MagicMock()
sys.modules["yfinance"] = MagicMock()
sys.modules["plotly.graph_objects"] = MagicMock()
sys.modules["plotly.subplots"] = MagicMock()

# Mock st.columns
def mock_columns(spec, gap="small"):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]
sys.modules["streamlit"].columns = MagicMock(side_effect=mock_columns)

# Mock st.tabs
def mock_tabs(tabs):
    return [MagicMock() for _ in range(len(tabs))]
sys.modules["streamlit"].tabs = MagicMock(side_effect=mock_tabs)

# Mock st.sidebar.toggle
sys.modules["streamlit"].sidebar.toggle.return_value = False
sys.modules["streamlit"].toggle.return_value = False

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock st.cache_data
def mock_cache_data(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator
sys.modules["streamlit"].cache_data = mock_cache_data

# Ensure fetch_market_data returns None or raises exception so we don't proceed to UI logic
sys.modules["yfinance"].download.side_effect = Exception("Mocked error")

from app import generate_forecast

class TestForecast(unittest.TestCase):
    def test_forecast_basic(self):
        start_date = datetime(2023, 1, 1)
        last_price = 100.0
        last_std = 1.0
        days = 10

        dates, means, uppers, lowers = generate_forecast(start_date, last_price, last_std, days)

        self.assertEqual(len(dates), days)
        self.assertEqual(len(means), days)
        self.assertEqual(len(uppers), days)
        self.assertEqual(len(lowers), days)

        # Check first value
        drift = 0.0003
        expected_mean_0 = last_price * ((1 + drift) ** 1)
        self.assertAlmostEqual(means[0], expected_mean_0)

        # Check width logic for first day
        time_factor = np.sqrt(1)
        width = (1.28 * last_std) + (last_std * 0.1 * time_factor)
        self.assertAlmostEqual(uppers[0], means[0] + width)
        self.assertAlmostEqual(lowers[0], means[0] - width)

    def test_forecast_values_increase(self):
        # drift is positive, so mean should increase
        start_date = datetime(2023, 1, 1)
        last_price = 100.0
        last_std = 1.0
        days = 5

        dates, means, uppers, lowers = generate_forecast(start_date, last_price, last_std, days)

        for i in range(days - 1):
            self.assertLess(means[i], means[i+1])
            # Width also increases as sqrt(i) increases
            width_i = uppers[i] - means[i]
            width_next = uppers[i+1] - means[i+1]
            self.assertLess(width_i, width_next)

if __name__ == '__main__':
    unittest.main()
