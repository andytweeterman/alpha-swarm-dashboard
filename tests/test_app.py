import pytest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
sys.modules["streamlit"] = MagicMock()
# Mock cache_data decorator
sys.modules["streamlit"].cache_data = lambda func: func
sys.modules["streamlit"].cache_data = lambda ttl=3600: lambda func: func
sys.modules["streamlit"].set_page_config = MagicMock()
sys.modules["streamlit"].sidebar = MagicMock()
sys.modules["streamlit"].toggle.return_value = False
sys.modules["streamlit"].sidebar.toggle.return_value = False

# Fix mocks for unpacking
def mock_columns(spec, gap="small"):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, (list, tuple)):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

sys.modules["streamlit"].columns.side_effect = mock_columns

def mock_tabs(tabs):
    return [MagicMock() for _ in range(len(tabs))]

sys.modules["streamlit"].tabs.side_effect = mock_tabs


# Import functions from app.py
from app import calc_governance, calc_ppo, calc_cone, generate_forecast

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


def test_generate_forecast():
    start_date = datetime(2023, 1, 1)
    last_price = 100.0
    last_std = 2.0
    days = 30

    future_dates, future_mean, future_upper, future_lower = generate_forecast(start_date, last_price, last_std, days)

    # Check lengths
    assert len(future_dates) == days
    assert len(future_mean) == days
    assert len(future_upper) == days
    assert len(future_lower) == days

    # Check date sequence
    assert future_dates[0] == start_date + timedelta(days=1)
    assert future_dates[-1] == start_date + timedelta(days=days)

    # Check logic (Upper > Mean > Lower)
    for i in range(days):
        assert future_upper[i] > future_mean[i]
        assert future_mean[i] > future_lower[i]

    # Check drift (mean should slightly increase)
    assert future_mean[-1] > last_price

    # Test with custom days
    days_custom = 10
    future_dates_custom, _, _, _ = generate_forecast(start_date, last_price, last_std, days_custom)
    assert len(future_dates_custom) == days_custom
