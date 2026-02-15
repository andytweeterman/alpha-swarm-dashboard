import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
from unittest.mock import MagicMock
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st

# Mock cache_data decorator to handle @st.cache_data(ttl=...)
mock_st.cache_data = lambda ttl=3600: lambda func: func

# Mock page config so set_page_config doesn't crash if called
mock_st.set_page_config = MagicMock()

# Mock sidebar
mock_st.sidebar = MagicMock()
mock_st.sidebar.toggle.return_value = False

# Mock session state as a dict
mock_st.session_state = {}

# Mock columns to support unpacking
def mock_columns(spec, gap="small"):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]
mock_st.columns.side_effect = mock_columns

# Mock tabs to support unpacking
def mock_tabs(tabs):
    return [MagicMock() for _ in range(len(tabs))]
mock_st.tabs.side_effect = mock_tabs

# Mock context managers (spinner, popover, expander)
mock_st.spinner.return_value.__enter__.return_value = None
mock_st.spinner.return_value.__exit__.return_value = None

mock_st.popover.return_value.__enter__.return_value = MagicMock()
mock_st.popover.return_value.__exit__.return_value = None

mock_st.expander.return_value.__enter__.return_value = MagicMock()
mock_st.expander.return_value.__exit__.return_value = None

# Mock toggle return value to avoid KeyError in theme_config
mock_st.toggle.return_value = False

# Import functions from app.py
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

    # Needs a MultiIndex or just columns named 'Close'?
    # The function does: closes = data['Close']

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
