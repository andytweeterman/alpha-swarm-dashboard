import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock, patch

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
sys.modules["streamlit"] = MagicMock()
# Mock st.cache_data for use with arguments
sys.modules["streamlit"].cache_data = lambda ttl=3600: lambda func: func
# Mock page config so set_page_config doesn't crash if called
sys.modules["streamlit"].set_page_config = MagicMock()
# Mock sidebar
sys.modules["streamlit"].sidebar = MagicMock()
# Mock toggle return value to avoid KeyError in theme_config
sys.modules["streamlit"].toggle.return_value = False
sys.modules["streamlit"].sidebar.toggle.return_value = False

# Fix st.columns and st.tabs to return iterables
def mock_columns(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, (list, tuple)):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

sys.modules["streamlit"].columns.side_effect = mock_columns
sys.modules["streamlit"].tabs.side_effect = lambda tabs: [MagicMock() for _ in tabs]

# Import functions from app.py
# We import app after mocking streamlit to ensure top-level code runs with mocks
from app import calc_governance, calc_ppo, calc_cone, fetch_market_data

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

    # Check simple logic: Upper > Lower (where defined, first 20 might be NaN)
    valid = upper.dropna()
    assert (valid > lower[valid.index]).all()

def test_fetch_market_data_error():
    # Mock yfinance.download to raise an exception
    with patch('app.yf.download') as mock_download:
        mock_download.side_effect = Exception("API Error")

        result = fetch_market_data()

        assert result is None
        mock_download.assert_called_once()
