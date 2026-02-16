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
mock_st.cache_data = mock_cache_data
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
mock_yf = MagicMock()
sys.modules["yfinance"] = mock_yf
mock_yf.download.return_value = None
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

# Import functions from logic.py and styles.py
from logic import calc_governance, calc_ppo, calc_cone
from styles import get_base64_image

def test_governance_calculation():
    dates = pd.date_range("2020-01-01", periods=100)

    # We'll create a DataFrame for 'Close' prices
    closes = pd.DataFrame(index=dates)
    closes["HYG"] = np.random.rand(100) * 100
    closes["IEF"] = np.random.rand(100) * 100
    closes["^VIX"] = np.random.rand(100) * 20
    closes["RSP"] = np.random.rand(100) * 100
    closes["SPY"] = np.random.rand(100) * 400
    closes["DX-Y.NYB"] = np.random.rand(100) * 100

    # Combine into a MultiIndex DataFrame if that's what yf.download returns,
    # app.py: closes = full_data['Close']
    # So full_data needs a 'Close' column which returns the closes DF.

    full_data = pd.DataFrame(closes.values, index=closes.index, columns=closes.columns)
    # Simulate data['Close'] access
    # We can just make full_data have 'Close' key access to return closes
    # Or properly construct MultiIndex
    full_data = pd.concat([closes], axis=1, keys=['Close'])

    # We can simulate this with a dictionary or a DataFrame with a MultiIndex.
    # Let's use a dictionary-like object since data['Close'] is what matters.
    data = {'Close': closes}

    gov_df, status, color, reason = calc_governance(data)

    assert status in ["DEFENSIVE MODE", "CAUTION", "WATCHLIST", "COMFORT ZONE"]
    assert color in ["#f93e3e", "#ffaa00", "#f1c40f", "#00d26a"]
    # Updated to match logic.py's tuned logic
    assert reason in [
        "Structural Failure Confirmed",
        "Extreme Volatility",
        "Credit/Currency Stress",
        "Elevated Volatility",
        "Market Breadth Narrowing",
        "System Integrity Nominal",
        "Data Feed Unavailable",
        "Feed Disconnected"
    ]

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
        # Create a dummy image in the current directory (which is base_dir when running tests from root?
        # No, get_base64_image uses __file__ of styles.py).
        # styles.py is in root. Tests are in tests/.
        # os.getcwd() is root.
        # styles.py __file__ will be ./styles.py.

        # We need to create a file in the same directory as styles.py for it to be considered "valid".
        # Since styles.py is in root, we create it in root.

        dummy_img = "dummy_test_image.png"
        with open(dummy_img, "wb") as f:
            f.write(b"dummy image content")

        try:
            result_valid = get_base64_image(dummy_img)
            assert result_valid is not None, "Should accept valid file in base directory"
        finally:
            if os.path.exists(dummy_img):
                os.remove(dummy_img)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
