import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
from unittest.mock import MagicMock
sys.modules["streamlit"] = MagicMock()
# Mock cache_data decorator
sys.modules["streamlit"].cache_data = lambda func: func
# Mock st.cache_data for use
sys.modules["streamlit"].cache_data = lambda ttl=3600: lambda func: func
# Mock page config so set_page_config doesn't crash if called
sys.modules["streamlit"].set_page_config = MagicMock()
# Mock sidebar
sys.modules["streamlit"].sidebar = MagicMock()
# Mock toggle return value to avoid KeyError in theme_config
sys.modules["streamlit"].toggle.return_value = False
sys.modules["streamlit"].sidebar.toggle.return_value = False # In case I used st.sidebar.toggle

# Mock columns to return a list of mocks when unpacked
def mock_columns(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, (list, tuple)):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock(), MagicMock()] # Fallback for other cases

sys.modules["streamlit"].columns.side_effect = mock_columns

# Mock tabs to return a list of mocks
def mock_tabs(tabs, **kwargs):
    return [MagicMock() for _ in range(len(tabs))]

sys.modules["streamlit"].tabs.side_effect = mock_tabs


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
