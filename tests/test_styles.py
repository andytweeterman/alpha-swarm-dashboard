import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestStyles(unittest.TestCase):
    def setUp(self):
        # Create fresh mocks
        self.mock_st = MagicMock()
        self.mock_plotly = MagicMock()
        self.mock_plotly_go = MagicMock()
        self.mock_plotly.graph_objects = self.mock_plotly_go

        # Patch sys.modules
        # We need to patch it so that when we reload styles, it picks up our mocks
        self.modules_patcher = patch.dict(sys.modules, {
            "streamlit": self.mock_st,
            "plotly": self.mock_plotly,
            "plotly.graph_objects": self.mock_plotly_go
        })
        self.modules_patcher.start()

        # Reload styles to ensure it uses the fresh mocks
        # We must import inside setUp or try/except to handle if it's already imported
        try:
            import styles
            importlib.reload(styles)
        except ImportError:
            import styles

        self.styles = styles

        # Setup session state
        self.mock_st.session_state = {}

    def tearDown(self):
        self.modules_patcher.stop()

    def test_apply_theme_initializes_session_state(self):
        """Test that dark_mode is initialized to False if not present."""
        self.mock_st.session_state = {}
        self.styles.apply_theme()
        self.assertIn("dark_mode", self.mock_st.session_state)
        self.assertFalse(self.mock_st.session_state["dark_mode"])

    def test_apply_theme_light_mode(self):
        """Test light mode theme and markdown call."""
        self.mock_st.session_state = {"dark_mode": False}
        theme = self.styles.apply_theme()

        self.assertEqual(theme["BG_COLOR"], "#ffffff")
        self.assertEqual(theme["TEXT_PRIMARY"], "#000000")

        # Verify st.markdown called
        self.mock_st.markdown.assert_called_once()
        args, kwargs = self.mock_st.markdown.call_args
        css = args[0]
        self.assertIn("--bg-color: #ffffff", css)
        self.assertIn("--text-primary: #000000", css)

    def test_apply_theme_dark_mode(self):
        """Test dark mode theme and markdown call."""
        self.mock_st.session_state = {"dark_mode": True}
        theme = self.styles.apply_theme()

        self.assertEqual(theme["BG_COLOR"], "#0e1117")
        self.assertEqual(theme["TEXT_PRIMARY"], "#FFFFFF")

        # Verify st.markdown called
        self.mock_st.markdown.assert_called_once()
        args, kwargs = self.mock_st.markdown.call_args
        css = args[0]
        self.assertIn("--bg-color: #0e1117", css)
        self.assertIn("--text-primary: #FFFFFF", css)

if __name__ == '__main__':
    unittest.main()
