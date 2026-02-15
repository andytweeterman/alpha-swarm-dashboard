import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock, patch

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- MOCKING SETUP ---
# We must mock modules BEFORE importing app, because app.py runs code on import.

# Mock streamlit
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st

# Mock cache_data: handle both @st.cache_data and @st.cache_data(ttl=...)
def mock_cache_data(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
mock_st.cache_data = mock_cache_data

mock_st.toggle.return_value = False
mock_st.sidebar.toggle.return_value = False

# Handle st.columns and st.tabs to return iterables
def mock_columns(spec, gap="small"):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    else:
        return [MagicMock() for _ in range(len(spec))]

mock_st.columns.side_effect = mock_columns

def mock_tabs(tabs_list):
    return [MagicMock() for _ in range(len(tabs_list))]

mock_st.tabs.side_effect = mock_tabs

# Mock yfinance to prevent network calls during import
mock_yf = MagicMock()
sys.modules["yfinance"] = mock_yf
# Setup download to return empty DataFrame or something safe by default during import
mock_yf.download.return_value = pd.DataFrame()

# Now import app directly
# These functions exist in app.py as confirmed by reading the file
from app import calc_governance, calc_ppo, calc_cone, fetch_market_data

def test_fetch_market_data_success():
    """Test fetch_market_data returns data correctly when yfinance succeeds."""
    # Setup mock return value
    mock_data = pd.DataFrame({'Close': [100, 101]})
    mock_yf.download.return_value = mock_data

    # Call function
    result = fetch_market_data()

    # Assert
    assert result is not None
    assert not result.empty
    mock_yf.download.assert_called()

def test_fetch_market_data_failure():
    """Test fetch_market_data returns None when yfinance raises an exception."""
    # Setup mock to raise exception
    mock_yf.download.side_effect = Exception("Download failed")

    # Call function
    result = fetch_market_data()

    # Assert
    assert result is None

    # Reset side_effect for other tests
    mock_yf.download.side_effect = None
    mock_yf.download.return_value = pd.DataFrame()

def test_governance_calculation():
    """Test governance calculation logic."""
    # Create dummy data
    dates = pd.date_range("2020-01-01", periods=100)
    data = pd.DataFrame(index=dates)
    data["HYG"] = np.random.rand(100) * 100
    data["IEF"] = np.random.rand(100) * 100
    data["^VIX"] = np.random.rand(100) * 20
    data["RSP"] = np.random.rand(100) * 100
    data["SPY"] = np.random.rand(100) * 400
    data["DX-Y.NYB"] = np.random.rand(100) * 100

    # Simulate MultiIndex structure from yfinance
    df_close = data.copy()
    full_data = pd.concat([df_close], axis=1, keys=['Close'])

    gov_df, status, color, reason = calc_governance(full_data)

    assert status in ["EMERGENCY", "CAUTION", "WATCHLIST", "NORMAL OPS"]
    assert color in ["#f93e3e", "#ffaa00", "#f1c40f", "#00d26a"]
    assert reason in ["Structural/Policy Failure", "Market Divergence", "Elevated Risk Monitors", "System Integrity Nominal"]

def test_ppo_calculation():
    """Test PPO calculation."""
    dates = pd.date_range("2020-01-01", periods=100)
    price = pd.Series(np.random.rand(100) * 100, index=dates)

    ppo, sig, hist = calc_ppo(price)

    assert len(ppo) == 100
    assert len(sig) == 100
    assert len(hist) == 100

def test_cone_calculation():
    """Test Volatility Cone calculation."""
    dates = pd.date_range("2020-01-01", periods=100)
    price = pd.Series(np.random.rand(100) * 100, index=dates)

    sma, std, upper, lower = calc_cone(price)

    assert len(sma) == 100
    assert len(upper) == 100

    # Check simple logic: Upper > Lower (where defined, first 20 might be NaN)
    valid = upper.dropna()
    valid_lower = lower[valid.index]

    assert (valid > valid_lower).all()
