import sys
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import pytest

# Mock streamlit and yfinance before importing app
sys.modules['streamlit'] = MagicMock()
sys.modules['yfinance'] = MagicMock()

# Configure st.cache_data mock to behave as a decorator
def mock_cache_data(**kwargs):
    def decorator(func):
        return func
    return decorator

sys.modules['streamlit'].cache_data = mock_cache_data

# Import app after mocking
import app

# Fixture for data generation
@pytest.fixture
def mock_market_data():
    def _generate(length=30,
                  vix_val=20.0,
                  credit_delta_target=None,
                  breadth_delta_target=None,
                  dxy_delta_target=None):

        dates = pd.date_range(end=pd.Timestamp.now(), periods=length, freq='D')

        # Base values (constant)
        hyg = np.full(length, 100.0)
        ief = np.full(length, 100.0) # Ratio = 1.0
        vix = np.full(length, float(vix_val))
        rsp = np.full(length, 100.0)
        spy = np.full(length, 100.0) # Ratio = 1.0
        dxy = np.full(length, 100.0)

        # Apply deltas to the LAST value to trigger pct_change based on previous values
        # Previous values (e.g. at -10) remain at 100.

        if credit_delta_target is not None:
            # Credit_Delta is 10-period pct_change of HYG/IEF.
            # HYG[-1] needs to be 100 * (1 + credit_delta_target)
            hyg[-1] = 100.0 * (1.0 + credit_delta_target)

        if breadth_delta_target is not None:
            # Breadth_Delta is 20-period pct_change of RSP/SPY.
            rsp[-1] = 100.0 * (1.0 + breadth_delta_target)

        if dxy_delta_target is not None:
            # DXY_Delta is 5-period pct_change of DXY.
            dxy[-1] = 100.0 * (1.0 + dxy_delta_target)

        # Construct DataFrame
        df = pd.DataFrame({
            "HYG": hyg, "IEF": ief, "^VIX": vix,
            "RSP": rsp, "SPY": spy, "DX-Y.NYB": dxy
        }, index=dates)

        return {'Close': df}

    return _generate

def test_governance_normal_ops(mock_market_data):
    """Test that normal conditions result in NORMAL OPS status."""
    data = mock_market_data(vix_val=20.0)
    df, status, color, reason = app.calculate_governance_history(data)

    assert status == "NORMAL OPS"
    assert color == "#00CC00"
    assert reason == "System Integrity Nominal"

    latest = df.iloc[-1]
    assert not latest['Level_7']
    assert not latest['Level_5']
    assert not latest['Level_4']

def test_governance_level_4_watchlist_vix(mock_market_data):
    """Test Level 4 triggered by high VIX."""
    data = mock_market_data(vix_val=25.0)
    df, status, color, reason = app.calculate_governance_history(data)

    assert status == "WATCHLIST"
    assert color == "yellow"
    assert reason == "Elevated Risk Monitors"
    assert df['Level_4'].iloc[-1]
    assert not df['Level_5'].iloc[-1]

def test_governance_level_4_watchlist_breadth(mock_market_data):
    """Test Level 4 triggered by low Breadth Delta."""
    data = mock_market_data(breadth_delta_target=-0.03)
    df, status, color, reason = app.calculate_governance_history(data)

    assert status == "WATCHLIST"
    assert color == "yellow"
    assert reason == "Elevated Risk Monitors"
    assert df['Level_4'].iloc[-1]

def test_governance_level_5_caution(mock_market_data):
    """Test Level 5 triggered by VIX AND Breadth Delta."""
    data = mock_market_data(vix_val=25.0, breadth_delta_target=-0.03)
    df, status, color, reason = app.calculate_governance_history(data)

    assert status == "CAUTION"
    assert color == "orange"
    assert reason == "Market Divergence"
    assert df['Level_5'].iloc[-1]

def test_governance_level_7_emergency_credit(mock_market_data):
    """Test Level 7 triggered by low Credit Delta."""
    data = mock_market_data(credit_delta_target=-0.02)
    df, status, color, reason = app.calculate_governance_history(data)

    assert status == "EMERGENCY"
    assert color == "red"
    assert reason == "Structural/Policy Failure"
    assert df['Level_7'].iloc[-1]

def test_governance_level_7_emergency_dxy(mock_market_data):
    """Test Level 7 triggered by high DXY Delta."""
    data = mock_market_data(dxy_delta_target=0.03)
    df, status, color, reason = app.calculate_governance_history(data)

    assert status == "EMERGENCY"
    assert color == "red"
    assert reason == "Structural/Policy Failure"
    assert df['Level_7'].iloc[-1]

def test_governance_precedence(mock_market_data):
    """Test that Level 7 takes precedence over Level 5/4."""
    # Triggers for Level 5 (VIX=25, Breadth=-0.03) AND Level 7 (Credit=-0.02)
    data = mock_market_data(vix_val=25.0, breadth_delta_target=-0.03, credit_delta_target=-0.02)
    df, status, color, reason = app.calculate_governance_history(data)

    assert status == "EMERGENCY"
    assert color == "red"
    assert reason == "Structural/Policy Failure"

def test_get_strategist_update_missing_file():
    """Test fallback when update.csv is missing."""
    with patch('pandas.read_csv', side_effect=FileNotFoundError):
        date, title, text = app.get_strategist_update()
        assert date == "System Status"
        assert title == "Data Feed Offline"
        assert text == "Strategist update pending."

def test_get_strategist_update_valid_file():
    """Test parsing of valid update.csv."""
    mock_df = pd.DataFrame({
        'Key': ['Date', 'Title', 'Text'],
        'Value': ['2023-10-27', 'Weekly Update', 'Market is doing fine.\\nBuy low.']
    })
    with patch('pandas.read_csv', return_value=mock_df):
        date, title, text = app.get_strategist_update()
        assert date == '2023-10-27'
        assert title == 'Weekly Update'
        assert text == 'Market is doing fine.\n\nBuy low.'
