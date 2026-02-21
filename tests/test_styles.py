import pytest
import sys
import os
import re
from unittest.mock import MagicMock

# Add repo root to path so we can import styles
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock external dependencies before importing styles
# This is crucial because styles.py imports streamlit and plotly at the top level
sys.modules["streamlit"] = MagicMock()
sys.modules["plotly"] = MagicMock()
sys.modules["plotly.graph_objects"] = MagicMock()
sys.modules["plotly.subplots"] = MagicMock()

# Now import the module under test
from styles import render_market_card

def test_render_market_card_positive_delta():
    """Test render_market_card with a positive delta."""
    name = "AAPL"
    price = 150.00
    delta = 5.00
    pct = 3.45

    html = render_market_card(name, price, delta, pct)

    # Check essential parts
    assert name in html
    assert "150.00" in html
    assert "+5.00" in html
    assert "+3.45%" in html
    assert "var(--delta-up)" in html

    # Check accessible label
    expected_aria_label = f'aria-label="{name}: {price:,.2f}, up {abs(delta):.2f} ({pct:+.2f}%)"'
    assert expected_aria_label in html

def test_render_market_card_negative_delta():
    """Test render_market_card with a negative delta."""
    name = "BTC"
    price = 30000.50
    delta = -120.00
    pct = -0.40

    html = render_market_card(name, price, delta, pct)

    assert name in html
    assert "30,000.50" in html
    assert "-120.00" in html
    assert "-0.40%" in html
    assert "var(--delta-down)" in html

    expected_aria_label = f'aria-label="{name}: {price:,.2f}, down {abs(delta):.2f} ({pct:+.2f}%)"'
    assert expected_aria_label in html

def test_render_market_card_zero_delta():
    """Test render_market_card with zero delta."""
    name = "Stable"
    price = 1.00
    delta = 0.00
    pct = 0.00

    html = render_market_card(name, price, delta, pct)

    assert name in html
    assert "1.00" in html
    assert "+0.00" in html
    assert "+0.00%" in html
    assert "var(--delta-up)" in html

    expected_aria_label = f'aria-label="{name}: {price:,.2f}, up {abs(delta):.2f} ({pct:+.2f}%)"'
    assert expected_aria_label in html

def test_render_market_card_html_structure():
    """Test the HTML structure and accessibility attributes."""
    html = render_market_card("TEST", 100, 10, 10)

    # Check for accessibility roles and attributes
    assert 'role="group"' in html
    assert 'class="market-card"' in html
    assert 'class="market-ticker"' in html
    assert 'class="market-price"' in html
    assert 'class="market-delta"' in html

    # Check that inner elements are hidden from screen readers (since parent has label)
    assert html.count('aria-hidden="true"') >= 3

def test_render_market_card_security():
    """Test that inputs are escaped to prevent XSS."""
    name = '<script>alert("XSS")</script>'
    price = 100.00
    delta = 10.00
    pct = 10.00

    html = render_market_card(name, price, delta, pct)

    # The name should be escaped in the output
    assert "&lt;script&gt;" in html or "&#x3C;script&#x3E;" in html
    assert "<script>" not in html

    # Also check attribute injection
    name_quote = '"; bad_attr="true'
    html_quote = render_market_card(name_quote, price, delta, pct)

    # The quote should be escaped, preventing attribute injection
    assert '&quot;' in html_quote or "&#34;" in html_quote
