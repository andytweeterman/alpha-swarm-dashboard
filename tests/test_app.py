import pytest
import pandas as pd
import numpy as np
import sys
import os
import tempfile
from unittest.mock import MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
sys.modules["streamlit"] = MagicMock()
mock_st = sys.modules["streamlit"]

def mock_cache_data(*args, **kwargs):
    # If called as decorator without parens: @st.cache_data
    if len(args) == 1 and callable(args[0]):
        return args[0]
    # If called with parens: @st.cache_data(ttl=...)
    def decorator(func):
        return func
    return decorator

# Mock cache_data decorator
sys.modules["streamlit"].cache_data = mock_cache_data
# Mock page config so set_page_config doesn't crash if called
mock_st.set_page_config = MagicMock()
# Mock sidebar
mock_st.sidebar = MagicMock()
# Mock toggle return value
mock_st.toggle.return_value = False
mock_st.sidebar.toggle.return_value = False
# Mock session state
mock_st.session_state = {"dark_mode": False}

# Mock yfinance BEFORE importing app to avoid network calls
sys.modules["yfinance"] = MagicMock()
# Also mock plotly to avoid any plotting overhead if imported
sys.modules["plotly.graph_objects"] = MagicMock()
sys.modules["plotly.subplots"] = MagicMock()

# Mock st.columns to return a list of mocks based on input
def mock_columns(spec, gap="small"):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

sys.modules["streamlit"].columns = MagicMock(side_effect=mock_columns)

# Mock st.tabs
def mock_tabs(tabs):
    return [MagicMock() for _ in range(len(tabs))]

sys.modules["streamlit"].tabs = MagicMock(side_effect=mock_tabs)

# Mock st.spinner as context manager before importing app
mock_st.spinner.return_value.__enter__ = MagicMock()
mock_st.spinner.return_value.__exit__ = MagicMock()

# Import functions from app.py
from app import calc_governance, calc_ppo, calc_cone, get_base64_image

def test_governance_calculation():
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

    tuples = [('Close', col) for col in closes.columns]
    full_data = closes.copy()
    full_data.columns = pd.MultiIndex.from_tuples(tuples)

    gov_df, status, color, reason = calc_governance(full_data)

    assert status in ["DEFENSIVE MODE", "CAUTION", "WATCHLIST", "COMFORT ZONE"]
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

    valid = upper.dropna()
    assert (valid > lower[valid.index]).all()

def test_get_base64_image_security():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write("secret")
        tmp_path = tmp.name

    try:
        # Test 1: Absolute path outside allowed dir
        result = get_base64_image(tmp_path)
        # Should be None in secured version
        assert result is None, "Should reject absolute path outside base directory"

        # Test 2: Relative path traversal
        rel_path = os.path.relpath(tmp_path, os.getcwd())
        result_rel = get_base64_image(rel_path)
        assert result_rel is None, "Should reject relative path traversal"

        # Test 3: Valid file
        with open("dummy_test_image.png", "wb") as f:
            f.write(b"dummy image content")

        try:
            result_valid = get_base64_image("dummy_test_image.png")
            assert result_valid is not None, "Should accept valid file in base directory"
        finally:
            if os.path.exists("dummy_test_image.png"):
                os.remove("dummy_test_image.png")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
