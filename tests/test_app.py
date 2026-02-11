import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st

# Mock cache_data decorator
mock_st.cache_data = lambda func=None, ttl=None: (lambda f: f) if func is None else func

# Mock st.columns to return the correct number of columns
def mock_columns(spec, gap="small"):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list) or isinstance(spec, tuple):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

mock_st.columns.side_effect = mock_columns

# Mock st.tabs to return the correct number of tabs
def mock_tabs(tabs):
    return [MagicMock() for _ in range(len(tabs))]

mock_st.tabs.side_effect = mock_tabs

# Mock other streamlit functions
mock_st.set_page_config = MagicMock()
mock_st.sidebar = MagicMock()
mock_st.sidebar.toggle.return_value = False
# Allow st.toggle to be called with arguments and return False
mock_st.toggle.side_effect = lambda label, value=False: value
# Mock st.radio to return the first option or a default string
mock_st.radio.return_value = "Tactical (60-Day Zoom)"

# Import functions from app.py
# Note: importing app will execute the module-level code, which will use the mocks
# We need to make sure yfinance and other imports don't fail if they make network calls
# But usually yfinance is just imported, not used at top level except in functions.
# Wait, fetch_market_data is called in try-except block at end of file?

# Let's check app.py again.
# It calls fetch_market_data() inside a try-except block at the end.
# We should mock yfinance as well to avoid network calls during import.
sys.modules["yfinance"] = MagicMock()
# fetch_market_data returns None if exception, so we should ensure it returns a DataFrame or None
# app.py:
# full_data = fetch_market_data()
# ...
# if full_data is not None and not full_data.empty:

# If we mock yfinance, fetch_market_data might fail or return mock.
# Let's mock fetch_market_data in app.py if possible? No, we import app.
# But fetch_market_data is defined in app.py.

# We can mock yfinance.download to return an empty DataFrame or None
sys.modules["yfinance"].download.return_value = pd.DataFrame()

from app import calc_governance, calc_ppo, calc_cone

def test_governance_calculation():
    # Create dummy data
    dates = pd.date_range("2020-01-01", periods=100)
    data = pd.DataFrame(index=dates)
    data["HYG"] = np.random.rand(100) * 100
    data["IEF"] = np.random.rand(100) * 100
    data["^VIX"] = np.random.rand(100) * 20
    data["RSP"] = np.random.rand(100) * 100
    data["SPY"] = np.random.rand(100) * 400
    data["DX-Y.NYB"] = np.random.rand(100) * 100

    # The function expects a DataFrame with columns, and inside it does closes = data['Close']
    # So we need a DataFrame where columns are accessible directly if it was flat,
    # OR if it was MultiIndex.
    # app.py: closes = data['Close']
    # So the input data must have a 'Close' column (or be a MultiIndex with 'Close' level).

    # yfinance.download typically returns MultiIndex if multiple tickers, or just columns if one.
    # In app.py: tickers = ["SPY", ...] (multiple)
    # So data['Close'] returns a DataFrame with tickers as columns.

    # Let's construct input data as if it came from yfinance with MultiIndex
    midx = pd.MultiIndex.from_product([['Close'], ["HYG", "IEF", "^VIX", "RSP", "SPY", "DX-Y.NYB"]], names=['Price', 'Ticker'])
    # Construct DataFrame with this MultiIndex
    # Actually yfinance returns columns as (Price, Ticker)

    # Let's just create a DataFrame that simulates what `closes = data['Close']` would return.
    # Wait, the function takes `data` and does `closes = data['Close']`.

    # So we need to create a DataFrame `data` such that `data['Close']` returns the DataFrame with ticker columns.

    close_data = pd.DataFrame(index=dates)
    close_data["HYG"] = np.random.rand(100) * 100
    close_data["IEF"] = np.random.rand(100) * 100
    close_data["^VIX"] = np.random.rand(100) * 20
    close_data["RSP"] = np.random.rand(100) * 100
    close_data["SPY"] = np.random.rand(100) * 400
    close_data["DX-Y.NYB"] = np.random.rand(100) * 100

    # Create a mock object for data that returns close_data when ['Close'] is accessed
    mock_data = MagicMock()
    mock_data.__getitem__.side_effect = lambda key: close_data if key == 'Close' else None

    # But wait, app.py also checks if full_data is not None and not empty.

    # Let's try to pass a real DataFrame with MultiIndex columns
    # MultiIndex columns: ('Close', 'HYG'), ('Close', 'IEF'), etc.

    tuples = [('Close', col) for col in close_data.columns]
    data_mi = close_data.copy()
    data_mi.columns = pd.MultiIndex.from_tuples(tuples)

    gov_df, status, color, reason = calc_governance(data_mi)

    assert status in ["EMERGENCY", "CAUTION", "WATCHLIST", "NORMAL OPS"]
    assert color in ["#f93e3e", "#ffaa00", "#f1c40f", "#00d26a"]
    assert reason in ["Structural/Policy Failure", "Market Divergence", "Elevated Risk Monitors", "System Integrity Nominal"]

def test_ppo_calculation():
    dates = pd.date_range("2020-01-01", periods=100)
    price = pd.Series(np.random.rand(100) * 100, index=dates)

    ppo, sig, hist = calc_ppo(price)

    assert len(ppo) == 100
    assert len(sig) == 100
    assert len(hist) == 100

def test_cone_calculation():
    dates = pd.date_range("2020-01-01", periods=100)
    price = pd.Series(np.random.rand(100) * 100, index=dates)

    sma, std, upper, lower = calc_cone(price)

    assert len(sma) == 100
    assert len(upper) == 100

    # Check simple logic: Upper > Lower (where defined, first 20 might be NaN)
    valid = upper.dropna()
    assert (valid > lower[valid.index]).all()
