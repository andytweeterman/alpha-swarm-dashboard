import unittest
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before import (styles.py imports streamlit)
from unittest.mock import MagicMock
sys.modules["streamlit"] = MagicMock()
sys.modules["plotly.graph_objects"] = MagicMock()

import styles

class TestStylesAccessibility(unittest.TestCase):
    def test_relative_luminance(self):
        # White
        self.assertAlmostEqual(styles.relative_luminance("#FFFFFF"), 1.0, places=4)
        self.assertAlmostEqual(styles.relative_luminance("#ffffff"), 1.0, places=4)
        # Black
        self.assertAlmostEqual(styles.relative_luminance("#000000"), 0.0, places=4)
        # Red #FF0000
        # 0.2126 * 1 + 0 + 0 = 0.2126
        self.assertAlmostEqual(styles.relative_luminance("#FF0000"), 0.2126, places=4)
        # Green #00FF00
        self.assertAlmostEqual(styles.relative_luminance("#00FF00"), 0.7152, places=4)
        # Blue #0000FF
        self.assertAlmostEqual(styles.relative_luminance("#0000FF"), 0.0722, places=4)

    def test_get_best_text_color(self):
        # White BG -> Black Text
        self.assertEqual(styles.get_best_text_color("#FFFFFF"), "#000000")
        # Black BG -> White Text
        self.assertEqual(styles.get_best_text_color("#000000"), "#ffffff")

        # Yellow BG #FFFF00 -> Black Text
        # Lum: 0.2126 + 0.7152 = 0.9278
        # Contrast White: 1.05 / 0.9778 = 1.07
        # Contrast Black: 0.9778 / 0.05 = 19.5
        self.assertEqual(styles.get_best_text_color("#FFFF00"), "#000000")

        # Dark Blue #000088 -> White Text
        # Lum: Very low
        self.assertEqual(styles.get_best_text_color("#000088"), "#ffffff")

        # Status Colors
        # Red #f93e3e
        # Lum: ~0.4. Contrast Black > Contrast White.
        self.assertEqual(styles.get_best_text_color("#f93e3e"), "#000000")

        # Green #00d26a
        # Lum: ~0.6.
        # Contrast White: 1.05 / 0.65 = 1.6
        # Contrast Black: 0.65 / 0.05 = 13.0
        # Should be Black text.
        self.assertEqual(styles.get_best_text_color("#00d26a"), "#000000")

        # Yellow/Orange #ffaa00
        # High lum red + green. Should be Black text.
        self.assertEqual(styles.get_best_text_color("#ffaa00"), "#000000")

if __name__ == '__main__':
    unittest.main()
