import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import pandas as pd
import importlib

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestGetStrategistUpdate(unittest.TestCase):
    def setUp(self):
        # Create a fresh mock for streamlit
        self.mock_st = MagicMock()

        # Mock st.cache_data to be a pass-through decorator
        def mock_cache_data(*args, **kwargs):
            if len(args) == 1 and callable(args[0]):
                return args[0]
            def decorator(func):
                return func
            return decorator

        self.mock_st.cache_data = mock_cache_data

        # Patch sys.modules to use our mock
        # We use patch.dict to safely restore it later (though logic module will stay reloaded)
        self.st_patcher = patch.dict(sys.modules, {'streamlit': self.mock_st, 'yfinance': MagicMock()})
        self.st_patcher.start()

        # Reload logic to pick up the new mock
        import logic
        importlib.reload(logic)

        # Get the function from the reloaded module
        self.get_strategist_update = logic.get_strategist_update

        # Reset environment variables
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()

        # Initialize secrets as empty dict
        self.mock_st.secrets = {}

    def tearDown(self):
        self.env_patcher.stop()
        self.st_patcher.stop()

    @patch('pandas.read_csv')
    def test_env_var_url(self, mock_read_csv):
        # Case 1: STRATEGIST_SHEET_URL in os.environ
        test_url = "http://example.com/sheet.csv"
        os.environ["STRATEGIST_SHEET_URL"] = test_url

        mock_df = pd.DataFrame({'col': [1, 2]})
        mock_read_csv.return_value = mock_df

        result = self.get_strategist_update()

        mock_read_csv.assert_called_with(test_url)
        pd.testing.assert_frame_equal(result, mock_df)

    @patch('pandas.read_csv')
    def test_secrets_url(self, mock_read_csv):
        # Case 2: STRATEGIST_SHEET_URL in st.secrets (and not in env)
        test_url = "http://example.com/sheet_secret.csv"
        self.mock_st.secrets = {"STRATEGIST_SHEET_URL": test_url}

        mock_df = pd.DataFrame({'col': [3, 4]})
        mock_read_csv.return_value = mock_df

        result = self.get_strategist_update()

        mock_read_csv.assert_called_with(test_url)
        pd.testing.assert_frame_equal(result, mock_df)

    @patch('pandas.read_csv')
    def test_invalid_url_fallback(self, mock_read_csv):
        # Case 3: URL contains "INSERT_YOUR" -> fallback to local file
        invalid_url = "http://example.com/INSERT_YOUR_KEY/sheet.csv"
        os.environ["STRATEGIST_SHEET_URL"] = invalid_url

        # Mock os.path.exists to return True for local file
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            mock_df = pd.DataFrame({'col': [5, 6]})
            mock_read_csv.return_value = mock_df

            result = self.get_strategist_update()

            # verify it didn't use the invalid url
            call_args = mock_read_csv.call_args[0][0]
            self.assertTrue(call_args.endswith("update.csv"))
            pd.testing.assert_frame_equal(result, mock_df)

    @patch('pandas.read_csv')
    def test_local_file_fallback(self, mock_read_csv):
        # Case 4: No URL -> fallback to local file

        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            mock_df = pd.DataFrame({'col': [7, 8]})
            mock_read_csv.return_value = mock_df

            result = self.get_strategist_update()

            call_args = mock_read_csv.call_args[0][0]
            self.assertTrue(call_args.endswith("update.csv"))
            pd.testing.assert_frame_equal(result, mock_df)

    def test_no_data(self):
        # Case 5: No URL and local file doesn't exist -> None
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            result = self.get_strategist_update()
            self.assertIsNone(result)

    @patch('pandas.read_csv')
    def test_exception_handling(self, mock_read_csv):
        # Case 6: Exception during read_csv -> None
        os.environ["STRATEGIST_SHEET_URL"] = "http://valid.url"
        mock_read_csv.side_effect = Exception("Network error")

        result = self.get_strategist_update()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
