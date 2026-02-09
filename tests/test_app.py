import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add repo root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

# Import functions from app.py
from app import calculate_governance_history, calculate_ppo, calculate_cone

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

    gov_df, status, color, reason = calculate_governance_history(full_data)

    assert status in ["EMERGENCY", "CAUTION", "WATCHLIST", "NORMAL OPS"]
    assert color in ["red", "orange", "yellow", "#00CC00"]
    assert reason in ["Structural/Policy Failure", "Market Divergence", "Elevated Risk Monitors", "System Integrity Nominal"]

def test_ppo_calculation():
    dates = pd.date_range("2020-01-01", periods=100)
    price = pd.Series(np.random.rand(100) * 100, index=dates)

    ppo, sig, hist = calculate_ppo(price)

    assert len(ppo) == 100
    assert len(sig) == 100
    assert len(hist) == 100

def test_cone_calculation():
    dates = pd.date_range("2020-01-01", periods=100)
    price = pd.Series(np.random.rand(100) * 100, index=dates)

    sma, std, upper, lower = calculate_cone(price)

    assert len(sma) == 100
    assert len(upper) == 100

    # Check simple logic: Upper > Lower (where defined, first 20 might be NaN)
    valid = upper.dropna()
    assert (valid > lower[valid.index]).all()
