import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to sys.path to import calculations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculations import calculate_cone

def test_calculate_cone_basic():
    """Verify calculate_cone returns 4 series and correct types."""
    data = pd.Series(np.random.randn(100), index=pd.date_range("2023-01-01", periods=100))
    sma, std, upper, lower = calculate_cone(data)

    assert isinstance(sma, pd.Series)
    assert isinstance(std, pd.Series)
    assert isinstance(upper, pd.Series)
    assert isinstance(lower, pd.Series)
    assert len(sma) == 100
    assert len(std) == 100
    assert len(upper) == 100
    assert len(lower) == 100

def test_calculate_cone_constant_input():
    """Test with constant input. STD should be 0, Upper=Lower=SMA=Input."""
    data = pd.Series([10.0] * 50, index=pd.date_range("2023-01-01", periods=50))
    sma, std, upper, lower = calculate_cone(data)

    # Check after window size (index 19 is the 20th element)
    # Pandas rolling window size 20 means index 19 is the first valid result if min_periods=None

    subset_sma = sma.iloc[19:]
    subset_std = std.iloc[19:]
    subset_upper = upper.iloc[19:]
    subset_lower = lower.iloc[19:]

    assert (subset_sma == 10.0).all()
    # std should be very close to 0
    assert (subset_std < 1e-10).all()
    assert (subset_upper - 10.0 < 1e-10).all()
    assert (subset_lower - 10.0 < 1e-10).all()

def test_calculate_cone_logic():
    """Test calculation logic: upper = sma + 1.28*std, lower = sma - 1.28*std."""
    data = pd.Series(np.arange(100, dtype=float), index=pd.date_range("2023-01-01", periods=100))
    sma, std, upper, lower = calculate_cone(data)

    # We ignore the first 19 values which are NaN
    expected_upper = sma + (1.28 * std)
    expected_lower = sma - (1.28 * std)

    pd.testing.assert_series_equal(upper, expected_upper)
    pd.testing.assert_series_equal(lower, expected_lower)

def test_calculate_cone_short_series():
    """Test series shorter than window size (20)."""
    data = pd.Series(np.random.randn(10), index=pd.date_range("2023-01-01", periods=10))
    sma, std, upper, lower = calculate_cone(data)

    assert sma.isna().all()
    assert std.isna().all()
    assert upper.isna().all()
    assert lower.isna().all()

def test_calculate_cone_empty():
    """Test empty series."""
    data = pd.Series([], dtype=float)
    sma, std, upper, lower = calculate_cone(data)

    assert sma.empty
    assert std.empty
    assert upper.empty
    assert lower.empty

def test_calculate_cone_nan_handling():
    """Test input with NaNs."""
    data = pd.Series(np.random.randn(50), index=pd.date_range("2023-01-01", periods=50))
    data.iloc[25] = np.nan

    sma, std, upper, lower = calculate_cone(data)

    assert len(sma) == 50

    # The window including index 25 (e.g., index 25 itself) should result in NaN
    assert pd.isna(sma.iloc[25])

    # Check if index 45 is valid (window 26..45 does not include 25)
    if len(sma) > 45:
        assert not pd.isna(sma.iloc[45])
