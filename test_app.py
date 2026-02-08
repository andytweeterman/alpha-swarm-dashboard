import sys
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest

# Mock streamlit before importing app
mock_st = MagicMock()
# Ensure @st.cache_data acts as a pass-through decorator so we can test the function
def side_effect_cache_data(**kwargs):
    def decorator(func):
        return func
    return decorator
mock_st.cache_data.side_effect = side_effect_cache_data
sys.modules["streamlit"] = mock_st

# Import app logic
import app

@pytest.fixture
def sample_data():
    """Generates sample market data for testing."""
    dates = pd.date_range(end=datetime.now(), periods=100)
    tickers = ["SPY", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB"]

    # Create random data
    data = {}
    for ticker in tickers:
        # Generate some random walk price data
        price = 100 + np.cumsum(np.random.randn(100))
        if ticker == "^VIX":
             price = 15 + np.cumsum(np.random.randn(100)) # VIX range

        data[('Close', ticker)] = price
        data[('Open', ticker)] = price # Dummy
        data[('High', ticker)] = price # Dummy
        data[('Low', ticker)] = price # Dummy

    df = pd.DataFrame(data, index=dates)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df

def test_fetch_data():
    # Setup mock data with MultiIndex columns (Price, Ticker)
    dates = pd.date_range(end=datetime.now(), periods=10)
    tickers = ["SPY", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB"]
    price_types = ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']

    # Create a MultiIndex
    columns = pd.MultiIndex.from_product([price_types, tickers], names=['Price', 'Ticker'])

    # Create random data
    data = np.random.randn(len(dates), len(columns))
    mock_df = pd.DataFrame(data, index=dates, columns=columns)

    with patch('app.yf.download') as mock_download:
        mock_download.return_value = mock_df

        # Call function
        result = app.fetch_data()

        # Verify
        pd.testing.assert_frame_equal(result, mock_df)
        mock_download.assert_called_once()

        # Verify arguments
        args, kwargs = mock_download.call_args
        # args[0] should be the list of tickers
        assert set(args[0]) == set(tickers)
        assert 'start' in kwargs

        # Verify start date is approximately 5 years ago
        start_date = datetime.strptime(kwargs['start'], '%Y-%m-%d')
        expected_date = datetime.now() - timedelta(days=1825)
        # Allow for small difference due to execution time
        assert abs((start_date - expected_date).days) <= 1

        assert kwargs['progress'] is False

def test_calculate_ppo():
    # Test with a simple linear series
    dates = pd.date_range(start="2023-01-01", periods=50)
    price = pd.Series(np.linspace(100, 110, 50), index=dates)

    ppo, sig, hist = app.calculate_ppo(price)

    assert isinstance(ppo, pd.Series)
    assert isinstance(sig, pd.Series)
    assert isinstance(hist, pd.Series)
    assert len(ppo) == 50
    # PPO calculation involves EMA which needs some data points to stabilize but returns values for all points (nan at start?)
    # Pandas ewm with adjust=False starts from the first value.
    assert not ppo.isnull().all()

def test_calculate_cone():
    dates = pd.date_range(start="2023-01-01", periods=50)
    price = pd.Series(np.random.normal(100, 5, 50), index=dates)

    sma, std, upper, lower = app.calculate_cone(price)

    assert len(sma) == 50
    # SMA window is 20, so first 19 values should be NaN
    assert pd.isna(sma.iloc[18])
    assert not pd.isna(sma.iloc[19])

    # Check bands logic
    valid_idx = 20
    assert upper.iloc[valid_idx] > sma.iloc[valid_idx]
    assert lower.iloc[valid_idx] < sma.iloc[valid_idx]

def test_generate_forecast():
    start_date = datetime(2023, 1, 1)
    last_price = 100.0
    last_std = 2.0
    days = 30

    dates, means, uppers, lowers = app.generate_forecast(start_date, last_price, last_std, days)

    assert len(dates) == days
    assert len(means) == days
    assert len(uppers) == days
    assert len(lowers) == days

    # Check date progression
    assert dates[0] == start_date + timedelta(days=1)
    assert dates[-1] == start_date + timedelta(days=days)

    # Check drift (positive drift means mean should increase)
    assert means[-1] > means[0]

def test_calculate_governance_history_normal():
    # Ensure normal conditions
    # Modify data to be safe
    # Level 7: Credit_Delta < -0.015 OR DXY_Delta > 0.02
    # Level 5: VIX > 24 AND Breadth_Delta < -0.025

    # We need to control the inputs precisely to guarantee output
    # But calculate_governance_history uses rolling windows/pct_change.

    # Let's create a specific scenario where changes are small
    dates = pd.date_range(end=datetime.now(), periods=100)

    # Flat prices -> 0 change
    closes = pd.DataFrame(index=dates)
    closes["SPY"] = 100.0
    closes["HYG"] = 100.0
    closes["IEF"] = 100.0
    closes["^VIX"] = 15.0 # Safe VIX
    closes["RSP"] = 100.0
    closes["DX-Y.NYB"] = 100.0

    # Reconstruct clean data
    data = {}
    for col in closes.columns:
        data[('Close', col)] = closes[col]

    df = pd.DataFrame(data, index=dates)
    df.columns = pd.MultiIndex.from_tuples(df.columns)

    res_df, status, color, reason = app.calculate_governance_history(df)

    assert status == "NORMAL OPS"
    assert color == "#00CC00"

def test_calculate_governance_history_emergency():
    # Trigger Level 7: DXY_Delta > 0.02 (DXY Spike)
    dates = pd.date_range(end=datetime.now(), periods=100)

    closes = pd.DataFrame(index=dates)
    # Default values
    closes["SPY"] = 100.0
    closes["HYG"] = 100.0
    closes["IEF"] = 100.0
    closes["^VIX"] = 15.0
    closes["RSP"] = 100.0
    # DXY spike at the end
    # DXY_Delta is pct_change(5)
    # Make last 5 values increase by > 2%
    dxy = np.full(100, 100.0)
    dxy[-1] = 105.0 # 5% jump
    closes["DX-Y.NYB"] = dxy

    data = {}
    for col in closes.columns:
        data[('Close', col)] = closes[col]

    df = pd.DataFrame(data, index=dates)
    df.columns = pd.MultiIndex.from_tuples(df.columns)

    res_df, status, color, reason = app.calculate_governance_history(df)

    assert status == "EMERGENCY"
    assert color == "red"
    assert "Structural/Policy Failure" in reason
