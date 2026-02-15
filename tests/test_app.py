import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock, patch

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- MOCK STREAMLIT ---
# We must mock streamlit BEFORE importing app, because app.py executes code at module level.
st_mock = MagicMock()

def mock_columns(spec, gap="small"):
    # Return a list of mocks equal to the number of columns requested
    if isinstance(spec, int):
        count = spec
    else:
        count = len(spec)
    return [MagicMock() for _ in range(count)]

st_mock.columns.side_effect = mock_columns
st_mock.tabs.side_effect = lambda tabs: [MagicMock() for _ in tabs]
# Mock cache_data to just return the function
st_mock.cache_data = lambda ttl=None: lambda func: func
# Mock secrets
st_mock.secrets = {}

sys.modules["streamlit"] = st_mock

# --- MOCK YFINANCE ---
yf_mock = MagicMock()
yf_mock.download.return_value = pd.DataFrame()
sys.modules["yfinance"] = yf_mock

# Import functions from app.py
from app import calc_governance, calc_ppo, calc_cone, get_strategist_update

def test_governance_calculation():
    # Create dummy data
    dates = pd.date_range("2020-01-01", periods=100)

    # Create a DataFrame where columns are a MultiIndex with level 0 as 'Close'
    cols = pd.MultiIndex.from_product([['Close'], ["HYG", "IEF", "^VIX", "RSP", "SPY", "DX-Y.NYB"]])
    full_data = pd.DataFrame(np.random.rand(100, 6) * 100, index=dates, columns=cols)

    # calc_governance expects full_data
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

def test_get_strategist_update_env_var():
    # Mock os.environ
    expected_url = "https://example.com/sheet.csv"
    with patch.dict(os.environ, {"STRATEGIST_SHEET_URL": expected_url}):
        # Mock pd.read_csv to avoid network call
        with patch("pandas.read_csv") as mock_read_csv:
            mock_read_csv.return_value = pd.DataFrame({"Key": [], "Value": []})

            df = get_strategist_update()

            mock_read_csv.assert_called_with(expected_url)
            assert isinstance(df, pd.DataFrame)

def test_get_strategist_update_fallback():
    # Ensure env var is missing
    with patch.dict(os.environ, {}, clear=True):
        # Ensure secrets are missing
        st_mock.secrets = {}

        with patch("pandas.read_csv") as mock_read_csv:
            mock_read_csv.return_value = pd.DataFrame({"Key": [], "Value": []})

            df = get_strategist_update()

            mock_read_csv.assert_called_with("data/update.csv")
