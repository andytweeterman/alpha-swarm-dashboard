import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
st_mock = MagicMock()

# Setup mocks for unpacking
# st.columns: returns list of mocks based on input
def mock_columns(spec, gap="small"):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, (list, tuple)):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

st_mock.columns.side_effect = mock_columns

# st.tabs: returns list of mocks based on input
def mock_tabs(tabs):
    return [MagicMock() for _ in range(len(tabs))]

st_mock.tabs.side_effect = mock_tabs

# st.cache_data: decorator that returns the function
def mock_cache_data(ttl=3600):
    def decorator(func):
        return func
    return decorator

st_mock.cache_data = mock_cache_data

# Other mocks
st_mock.set_page_config = MagicMock()
st_mock.sidebar = MagicMock()
st_mock.toggle.return_value = False
st_mock.sidebar.toggle.return_value = False
st_mock.session_state = {}

sys.modules["streamlit"] = st_mock

# Now import app functions
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

    # calc_governance expects a DataFrame with MultiIndex columns (Price, Ticker)
    # yfinance download returns MultiIndex if multiple tickers.

    df_close = data.copy()
    full_data = pd.concat([df_close], axis=1, keys=['Close'])

    gov_df, status, color, reason = calc_governance(full_data)

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

    # Check logic: Upper > Lower (ignoring NaNs at start)
    valid = upper.dropna()
    # Ensure corresponding lower is valid and smaller
    if not valid.empty:
        assert (valid >= lower[valid.index]).all()
