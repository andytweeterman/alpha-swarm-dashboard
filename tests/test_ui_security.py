import sys
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
import pytest
import importlib

# Mock streamlit and yfinance before importing app
# We need to do this at module level so it applies when app is imported
sys.modules['streamlit'] = MagicMock()
sys.modules['yfinance'] = MagicMock()

# Configure st.cache_data mock to behave as a decorator
def mock_cache_data(**kwargs):
    def decorator(func):
        return func
    return decorator

sys.modules['streamlit'].cache_data = mock_cache_data

# Mock st.columns to return mocks that support context manager
def mock_columns(spec):
    cols = [MagicMock() for _ in range(len(spec) if isinstance(spec, list) else spec)]
    for col in cols:
        col.__enter__.return_value = col
        col.__exit__.return_value = None
    return cols

sys.modules['streamlit'].columns = mock_columns

# Mock st.expander to support context manager
mock_expander = MagicMock()
mock_expander.__enter__.return_value = mock_expander
mock_expander.__exit__.return_value = None
sys.modules['streamlit'].expander.return_value = mock_expander


# Fixture for data generation (copied from test_app.py)
@pytest.fixture
def mock_market_data():
    def _generate(length=30):
        dates = pd.date_range(end=pd.Timestamp.now(), periods=length, freq='D')

        # app.py treats the return value as a DataFrame (uses .index)
        # So we must return a DataFrame with MultiIndex columns.

        tickers = ["HYG", "IEF", "^VIX", "RSP", "SPY", "DX-Y.NYB", "^DJI", "^IXIC", "GC=F", "CL=F"]
        prices = ["Close", "Open", "High", "Low", "Adj Close", "Volume"]

        columns = pd.MultiIndex.from_product([prices, tickers], names=['Price', 'Ticker'])
        data_np = np.full((length, len(columns)), 100.0)

        df_multi = pd.DataFrame(data_np, index=dates, columns=columns)

        # Set specific values if needed (defaults are 100.0)
        # VIX defaults to 20.0 in the other fixture
        df_multi.loc[:, ('Close', '^VIX')] = 20.0

        return df_multi

    return _generate

def test_fix_verification(mock_market_data):
    """
    Test that the fix uses st.error/warning/success instead of unsafe HTML.
    This test ensures the security vulnerability is fixed.
    """
    # Setup mock data (Normal Ops -> Green -> st.success)
    data = mock_market_data()
    sys.modules['yfinance'].download.return_value = data

    # Reload app
    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])
    else:
        import app

    st_mock = sys.modules['streamlit']

    # Check absence of vulnerable call
    markdown_calls = st_mock.markdown.call_args_list
    found_vulnerable_call = False
    for call in markdown_calls:
        args, kwargs = call
        content = args[0] if args else kwargs.get('body', '')
        unsafe = kwargs.get('unsafe_allow_html', False)

        if "GOVERNANCE STATUS" in content and unsafe:
            found_vulnerable_call = True
            break

    assert not found_vulnerable_call, "Vulnerable st.markdown call still present!"

    # Check presence of safe call (st.success for Normal Ops)
    # The status should be NORMAL OPS
    success_calls = st_mock.success.call_args_list
    found_safe_call = False
    for call in success_calls:
        args, kwargs = call
        content = args[0] if args else kwargs.get('body', '')
        if "GOVERNANCE STATUS: NORMAL OPS" in content:
            found_safe_call = True
            break

    assert found_safe_call, "Expected st.success call for NORMAL OPS not found!"

def test_fix_verification_emergency(mock_market_data):
    """
    Test that EMERGENCY status uses st.error.
    """
    # Setup mock data for EMERGENCY (Level 7)
    # Credit Delta < -0.015
    # Credit Ratio = HYG/IEF
    # HYG drops
    data = mock_market_data(length=50)
    # Set HYG to drop at the end
    # data is a DataFrame
    # HYG is ('Close', 'HYG')

    # We need to calculate what HYG value gives < -1.5% delta over 10 days.
    # Previous HYG is 100.
    # New HYG < 100 * (1 - 0.015) = 98.5

    data.loc[data.index[-1], ('Close', 'HYG')] = 98.0

    sys.modules['yfinance'].download.return_value = data

    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])
    else:
        import app

    st_mock = sys.modules['streamlit']

    # Check for st.error
    error_calls = st_mock.error.call_args_list
    found_safe_call = False
    for call in error_calls:
        args, kwargs = call
        content = args[0] if args else kwargs.get('body', '')
        if "GOVERNANCE STATUS: EMERGENCY" in content:
            found_safe_call = True
            break

    assert found_safe_call, "Expected st.error call for EMERGENCY not found!"
