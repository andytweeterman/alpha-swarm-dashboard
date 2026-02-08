import pytest
import pandas as pd
import numpy as np
import sys
import os

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculations import calculate_ppo

def test_calculate_ppo_structure():
    """Test that the function returns 3 pandas Series with correct types and lengths."""
    # Create a dummy price series
    prices = pd.Series(np.random.randn(100) + 100, index=pd.date_range("2020-01-01", periods=100))

    ppo, signal, hist = calculate_ppo(prices)

    assert isinstance(ppo, pd.Series)
    assert isinstance(signal, pd.Series)
    assert isinstance(hist, pd.Series)
    assert len(ppo) == len(prices)
    assert len(signal) == len(prices)
    assert len(hist) == len(prices)

def test_calculate_ppo_constant():
    """Test that PPO converges to 0 for constant prices."""
    # Constant price
    prices = pd.Series([100.0] * 100)

    ppo, signal, hist = calculate_ppo(prices)

    # For a constant price series, EMA12 and EMA26 should be equal to the price (after initialization or immediately if adjust=False starts at price)
    # If EMA12 == EMA26, then PPO should be 0.

    # Check if all values are approximately 0
    assert (ppo.abs() < 1e-10).all()
    assert (signal.abs() < 1e-10).all()
    assert (hist.abs() < 1e-10).all()

def test_calculate_ppo_uptrend():
    """Test with a simple increasing trend."""
    # In an uptrend, EMA12 (faster) > EMA26 (slower), so PPO should be positive.
    prices = pd.Series(np.linspace(100, 200, 100))

    ppo, signal, hist = calculate_ppo(prices)

    # Skip the first few periods where EMAs are initializing/crossing
    # Though with adjust=False starting at the first value, they start equal (100).
    # Then next value is slightly higher. EMA12 reacts faster. So PPO > 0 immediately after first step.

    assert (ppo.iloc[1:] > 0).all()

def test_calculate_ppo_downtrend():
    """Test with a simple decreasing trend."""
    # In a downtrend, EMA12 < EMA26, so PPO should be negative.
    prices = pd.Series(np.linspace(200, 100, 100))

    ppo, signal, hist = calculate_ppo(prices)

    assert (ppo.iloc[1:] < 0).all()

def test_calculate_ppo_empty():
    """Test behavior with empty input."""
    prices = pd.Series([], dtype=float)

    ppo, signal, hist = calculate_ppo(prices)

    assert len(ppo) == 0
    assert len(signal) == 0
    assert len(hist) == 0
    assert ppo.empty
    assert signal.empty
    assert hist.empty

def test_calculate_ppo_nan():
    """Test handling of NaN values."""
    prices = pd.Series([100.0, 101.0, np.nan, 102.0, 103.0])

    ppo, signal, hist = calculate_ppo(prices)

    assert len(ppo) == len(prices)
    # With adjust=False, ewm usually propagates the previous value if NaN is encountered (depending on ignore_na default)
    # Pandas defaults ignore_na=False, which treats NaNs by just not updating the weighted average?
    # Actually, it seems to just propagate the previous value.
    # Let's verify that it produces a valid float or NaN, but more importantly doesn't crash.
    assert isinstance(ppo.iloc[2], float)

    # Check that subsequent calculations continue correctly
    assert not np.isnan(ppo.iloc[4])
