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
from unittest.mock import MagicMock
sys.modules["streamlit"] = MagicMock()

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
sys.modules["streamlit"].set_page_config = MagicMock()
# Mock sidebar
sys.modules["streamlit"].sidebar = MagicMock()
# Mock toggle return value to avoid KeyError in theme_config
sys.modules["streamlit"].toggle.return_value = False
sys.modules["streamlit"].sidebar.toggle.return_value = False # In case I used st.sidebar.toggle

# Configure columns to return a list of mocks when called
def mock_columns(spec, gap="small"):
    if isinstance(spec, int):
        count = spec
    else:
        count = len(spec)
    return [MagicMock() for _ in range(count)]

sys.modules["streamlit"].columns = MagicMock(side_effect=mock_columns)

# Configure tabs to return a list of mocks when called
def mock_tabs(tabs):
    return [MagicMock() for _ in range(len(tabs))]

sys.modules["streamlit"].tabs = MagicMock(side_effect=mock_tabs)

# Import functions from app.py
from app import calc_governance, calc_ppo, calc_cone

def test_governance_calculation():
    dates = pd.date_range("2020-01-01", periods=100)
    data = pd.DataFrame(index=dates)
    data["HYG"] = np.random.rand(100) * 100
    data["IEF"] = np.random.rand(100) * 100
    data["^VIX"] = np.random.rand(100) * 20
    data["RSP"] = np.random.rand(100) * 100
    data["SPY"] = np.random.rand(100) * 400
    data["DX-Y.NYB"] = np.random.rand(100) * 100

    tuples = [('Close', col) for col in data.columns]
    data.columns = pd.MultiIndex.from_tuples(tuples)

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
