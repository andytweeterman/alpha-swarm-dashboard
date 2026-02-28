import sys
import os
import unittest
import importlib
from unittest.mock import MagicMock, patch

# Add repo root to path so we can import styles
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock external dependencies before ANY importing of styles to support restricted environments
mock_streamlit = MagicMock()
mock_plotly = MagicMock()
mock_plotly_go = MagicMock()

sys.modules['streamlit'] = mock_streamlit
sys.modules['plotly'] = mock_plotly
sys.modules['plotly.graph_objects'] = mock_plotly_go

import styles

class TestStyles(unittest.TestCase):
    def setUp(self):
        # Ensure styles is reloaded with mocks active
        self.styles = importlib.reload(styles)

    @patch('styles.go')
    def test_render_sparkline(self, mock_go):
        # Create a mock for pandas Series
        mock_data = MagicMock()
        mock_data.index = [1, 2, 3]

        # Call the function
        line_color = '#ffaa00'
        fig = self.styles.render_sparkline(mock_data, line_color)

        # Verify go.Figure() was called
        mock_go.Figure.assert_called_once()

        # Figure object returned by the function should be the return value of go.Figure()
        mock_fig = mock_go.Figure.return_value
        self.assertEqual(fig, mock_fig)

        # Verify go.Scatter() was called with correct arguments
        mock_go.Scatter.assert_called_once_with(
            x=mock_data.index,
            y=mock_data,
            mode='lines',
            line=dict(color=line_color, width=2),
            hoverinfo='skip'
        )

        # Verify fig.add_trace() was called with the result of go.Scatter()
        mock_scatter = mock_go.Scatter.return_value
        mock_fig.add_trace.assert_called_once_with(mock_scatter)

        # Verify fig.update_layout() was called with correct parameters
        mock_fig.update_layout.assert_called_once_with(
            height=40,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

if __name__ == '__main__':
    unittest.main()
