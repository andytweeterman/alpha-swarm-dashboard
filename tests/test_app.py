import pytest
import pandas as pd
import numpy as np
from app import calculate_ppo

def test_calculate_ppo_normal_data():
    """Test with normal data (length > 26)."""
    np.random.seed(42)
    price = pd.Series(np.random.rand(50) * 100 + 100)
    ppo, sig, hist = calculate_ppo(price)

    assert len(ppo) == 50
    assert len(sig) == 50
    assert len(hist) == 50
    assert isinstance(ppo, pd.Series)
    assert not ppo.isnull().all()

def test_calculate_ppo_short_data():
    """Test with short data (length < 26)."""
    price = pd.Series([100.0, 101.0, 102.0, 101.0, 100.0])
    ppo, sig, hist = calculate_ppo(price)

    assert len(ppo) == 5
    assert len(sig) == 5
    assert len(hist) == 5
    # Pandas ewm adjust=False starts calculating immediately
    assert not ppo.isnull().all()

def test_calculate_ppo_very_short_data():
    """Test with very short data (1 point)."""
    price = pd.Series([100.0])
    ppo, sig, hist = calculate_ppo(price)

    assert len(ppo) == 1
    # PPO calculation: ema12=100, ema26=100 -> (100-100)/100 = 0
    assert ppo.iloc[0] == 0.0

def test_calculate_ppo_empty_data():
    """Test with empty data."""
    price = pd.Series([], dtype=float)
    ppo, sig, hist = calculate_ppo(price)

    assert len(ppo) == 0
    assert len(sig) == 0
    assert len(hist) == 0

def test_calculate_ppo_nan_data():
    """Test with data containing NaNs."""
    price = pd.Series([100.0, np.nan, 102.0, 101.0, 100.0])
    ppo, sig, hist = calculate_ppo(price)

    assert len(ppo) == 5
    # Ensure no crash

def test_calculate_ppo_zero_data():
    """Test with data containing zeros (division by zero risk)."""
    price = pd.Series([0.0, 0.0, 0.0])
    ppo, sig, hist = calculate_ppo(price)

    # Expect NaNs because of division by zero
    assert ppo.isnull().all()
    assert sig.isnull().all()
    assert hist.isnull().all()
