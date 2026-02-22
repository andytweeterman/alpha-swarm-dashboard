
import unittest
import pandas as pd
import numpy as np
from styles import render_sparkline_svg

class TestSparklineSVG(unittest.TestCase):
    def test_render_sparkline_svg_normal_data(self):
        # 1. Setup
        data = pd.Series([10, 20, 15, 25, 30])
        color = "#FF0000"

        # 2. Execute
        svg = render_sparkline_svg(data, color)

        # 3. Verify
        self.assertIn("<svg", svg)
        self.assertIn(f'stroke="{color}"', svg)
        self.assertIn('viewBox="0 0 300 40"', svg)
        self.assertIn('preserveAspectRatio="none"', svg)
        self.assertIn('vector-effect="non-scaling-stroke"', svg)

        # Check points
        # normalized: 0, 0.5, 0.25, 0.75, 1.0
        # y: 38, 20, 29, 11, 2
        # x_step: 300 / 4 = 75
        # 0,38 75,20 150,29 225,11 300,2
        self.assertIn('points="0.0,38.0 75.0,20.0 150.0,29.0 225.0,11.0 300.0,2.0"', svg)

    def test_render_sparkline_svg_empty(self):
        data = pd.Series([], dtype=float)
        svg = render_sparkline_svg(data, "#000000")
        self.assertEqual(svg, "")

    def test_render_sparkline_svg_single_point(self):
        data = pd.Series([100])
        svg = render_sparkline_svg(data, "#00FF00")

        # Single point handling
        # y_min=100, y_max=100, range=1.0
        # normalized = 0
        # y = 38
        # x_step = 0 (len=1)
        # point: 0.0, 38.0
        self.assertIn('points="0.0,38.0"', svg)

    def test_render_sparkline_svg_constant_values(self):
        data = pd.Series([10, 10, 10])
        svg = render_sparkline_svg(data, "#0000FF")

        # y_min=10, y_max=10, range=1.0
        # normalized = 0
        # y = 38
        # x_step = 150
        # 0.0,38.0 150.0,38.0 300.0,38.0
        self.assertIn('points="0.0,38.0 150.0,38.0 300.0,38.0"', svg)

if __name__ == '__main__':
    unittest.main()
