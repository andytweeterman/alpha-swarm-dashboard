import unittest
import sys
import os
from unittest.mock import MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit and plotly before importing styles
sys.modules["streamlit"] = MagicMock()
sys.modules["plotly"] = MagicMock()
sys.modules["plotly.graph_objects"] = MagicMock()

from styles import render_market_card

class TestRenderMarketCard(unittest.TestCase):
    def test_render_market_card_positive_delta(self):
        name = "S&P 500"
        price = 4500.00
        delta = 10.00
        pct = 0.25

        result = render_market_card(name, price, delta, pct)

        self.assertIn('aria-label="S&P 500: 4,500.00, up 10.00 (+0.25%)"', result)
        self.assertIn('style="color: var(--delta-up);"', result)
        self.assertIn('>+10.00 (+0.25%)<', result)
        self.assertIn('aria-hidden="true">S&P 500<', result)
        self.assertIn('aria-hidden="true">4,500.00<', result)

    def test_render_market_card_negative_delta(self):
        name = "NASDAQ"
        price = 14000.50
        delta = -150.25
        pct = -1.05

        result = render_market_card(name, price, delta, pct)

        self.assertIn('aria-label="NASDAQ: 14,000.50, down 150.25 (-1.05%)"', result)
        self.assertIn('style="color: var(--delta-down);"', result)
        self.assertIn('>-150.25 (-1.05%)<', result)
        self.assertIn('aria-hidden="true">NASDAQ<', result)
        self.assertIn('aria-hidden="true">14,000.50<', result)

    def test_render_market_card_zero_delta(self):
        name = "DOW"
        price = 35000.00
        delta = 0.00
        pct = 0.00

        result = render_market_card(name, price, delta, pct)

        self.assertIn('aria-label="DOW: 35,000.00, up 0.00 (+0.00%)"', result)
        self.assertIn('style="color: var(--delta-up);"', result)
        self.assertIn('>+0.00 (+0.00%)<', result)
        self.assertIn('aria-hidden="true">DOW<', result)
        self.assertIn('aria-hidden="true">35,000.00<', result)

if __name__ == '__main__':
    unittest.main()
