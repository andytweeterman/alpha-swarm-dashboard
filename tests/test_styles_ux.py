import sys
import os
import pytest
from unittest.mock import MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import
sys.modules["streamlit"] = MagicMock()
# Mock plotly
sys.modules["plotly"] = MagicMock()
sys.modules["plotly.graph_objects"] = MagicMock()

from styles import relative_luminance, get_contrast_ratio, get_best_text_color

def test_relative_luminance():
    assert relative_luminance("#FFFFFF") == 1.0
    assert relative_luminance("#000000") == 0.0
    # Red 255, 0, 0 -> 0.2126
    assert abs(relative_luminance("#FF0000") - 0.2126) < 0.001
    # Green 0, 255, 0 -> 0.7152
    assert abs(relative_luminance("#00FF00") - 0.7152) < 0.001
    # Blue 0, 0, 255 -> 0.0722
    assert abs(relative_luminance("#0000FF") - 0.0722) < 0.001

def test_get_contrast_ratio():
    # Black and White
    assert abs(get_contrast_ratio("#000000", "#FFFFFF") - 21.0) < 0.1
    # White and White
    assert get_contrast_ratio("#FFFFFF", "#FFFFFF") == 1.0

def test_get_best_text_color():
    # Dark background -> White text
    assert get_best_text_color("#000000") == "#FFFFFF"
    assert get_best_text_color("#333333") == "#FFFFFF"
    assert get_best_text_color("#000033") == "#FFFFFF"

    # Light background -> Black text
    assert get_best_text_color("#FFFFFF") == "#000000"
    assert get_best_text_color("#FFFF00") == "#000000" # Yellow
    assert get_best_text_color("#f1c40f") == "#000000" # Watchlist Yellow

    # App specific colors
    assert get_best_text_color("#00d26a") == "#000000" # Comfort Zone (Green)
    assert get_best_text_color("#ffaa00") == "#000000" # Caution (Orange)
    assert get_best_text_color("#f93e3e") == "#000000" # Defensive (Red) - Black has better contrast than White here
