import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock, patch

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- MOCKING SETUP ---
# Create a robust mock for Streamlit
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st

# Configure st.columns and st.tabs to return lists of mocks
def side_effect_columns(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

mock_st.columns.side_effect = side_effect_columns
mock_st.tabs.side_effect = lambda tabs: [MagicMock() for _ in tabs]
# Mock st.cache_data decorator to just execute function
mock_st.cache_data = lambda **kwargs: lambda func: func
# Mock page config so set_page_config doesn't crash if called
mock_st.set_page_config = MagicMock()
# Mock sidebar
mock_st.sidebar = MagicMock()
# Mock toggle return value
mock_st.toggle.return_value = False
mock_st.sidebar.toggle.return_value = False
# Mock session state
mock_st.session_state = {}

# Mock yfinance BEFORE importing app to avoid network calls
sys.modules["yfinance"] = MagicMock()
# Also mock plotly to avoid any plotting overhead if imported
sys.modules["plotly.graph_objects"] = MagicMock()
sys.modules["plotly.subplots"] = MagicMock()

# --- IMPORT APP ---
# Now we can import app safely
from app import calc_governance, calc_ppo, calc_cone

# --- TESTS ---

def test_governance_calculation():
    # Create dummy data
    dates = pd.date_range("2020-01-01", periods=100)
    # Create a MultiIndex DataFrame as expected by calc_governance accessing data['Close']
    # Wait, calc_governance does: closes = data['Close']
    # So data needs to have a 'Close' column which is a DataFrame or Series with columns like HYG, IEF, etc.

    # We'll create a DataFrame for 'Close' prices
    closes = pd.DataFrame(index=dates)
    closes["HYG"] = np.random.rand(100) * 100
    closes["IEF"] = np.random.rand(100) * 100
    closes["^VIX"] = np.random.rand(100) * 20
    closes["RSP"] = np.random.rand(100) * 100
    closes["SPY"] = np.random.rand(100) * 400
    closes["DX-Y.NYB"] = np.random.rand(100) * 100

    # Combine into a MultiIndex DataFrame if that's what yf.download returns,
    # but based on app.py: closes = full_data['Close']
    # If full_data is a MultiIndex DF with top level 'Price', 'Ticker', then full_data['Close'] returns a DF with tickers as columns.

    # Let's construct full_data such that full_data['Close'] returns our closes DF.
    full_data = pd.concat([closes], axis=1, keys=['Close'])

    # Verify structure matches expectation
    assert 'Close' in full_data.columns
    assert 'HYG' in full_data['Close'].columns

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
    # Align indices just in case
    lower_valid = lower[valid.index]
    assert (valid > lower_valid).all()
