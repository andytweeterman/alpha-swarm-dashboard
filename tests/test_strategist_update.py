import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

# Mock streamlit before import
sys.modules["streamlit"] = MagicMock()
mock_st = sys.modules["streamlit"]

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic import get_strategist_update

class TestStrategistUpdate(unittest.TestCase):
    def setUp(self):
        # Reset st.secrets for each test
        mock_st.secrets = {}

    @patch('logic.pd.read_csv')
    @patch('logic.os.environ.get')
    def test_reads_from_environ(self, mock_env_get, mock_read_csv):
        mock_env_get.return_value = "http://valid.url"
        mock_df = pd.DataFrame({"col": [1]})
        mock_read_csv.return_value = mock_df

        result = get_strategist_update()

        self.assertEqual(result.iloc[0]["col"], 1)
        mock_read_csv.assert_called_once_with("http://valid.url")

    @patch('logic.pd.read_csv')
    @patch('logic.os.environ.get')
    def test_reads_from_secrets(self, mock_env_get, mock_read_csv):
        mock_env_get.return_value = None
        # Mocking st.secrets which is imported in logic as st.secrets
        # We need to mock the dictionary 'in' check and dictionary access
        with patch('logic.st.secrets', {"STRATEGIST_SHEET_URL": "http://secret.url"}):
            mock_df = pd.DataFrame({"col": [2]})
            mock_read_csv.return_value = mock_df

            result = get_strategist_update()

            self.assertEqual(result.iloc[0]["col"], 2)
            mock_read_csv.assert_called_once_with("http://secret.url")

    @patch('logic.pd.read_csv')
    @patch('logic.os.path.exists')
    @patch('logic.os.environ.get')
    def test_falls_back_to_local_when_insert_your(self, mock_env_get, mock_exists, mock_read_csv):
        mock_env_get.return_value = "http://INSERT_YOUR_URL"
        mock_exists.return_value = True
        mock_df = pd.DataFrame({"col": [3]})
        mock_read_csv.return_value = mock_df

        result = get_strategist_update()

        self.assertEqual(result.iloc[0]["col"], 3)
        mock_read_csv.assert_called_once_with(os.path.join("data", "update.csv"))

    @patch('logic.pd.read_csv')
    @patch('logic.os.path.exists')
    @patch('logic.os.environ.get')
    def test_falls_back_to_local_when_no_url(self, mock_env_get, mock_exists, mock_read_csv):
        mock_env_get.return_value = None
        # no secrets
        mock_exists.return_value = True
        mock_df = pd.DataFrame({"col": [4]})
        mock_read_csv.return_value = mock_df

        result = get_strategist_update()

        self.assertEqual(result.iloc[0]["col"], 4)
        mock_read_csv.assert_called_once_with(os.path.join("data", "update.csv"))

    @patch('logic.os.path.exists')
    @patch('logic.os.environ.get')
    def test_returns_none_if_local_not_exists(self, mock_env_get, mock_exists):
        mock_env_get.return_value = None
        mock_exists.return_value = False

        result = get_strategist_update()

        self.assertIsNone(result)

    @patch('logic.os.environ.get')
    def test_handles_exception(self, mock_env_get):
        mock_env_get.side_effect = Exception("Test exception")

        result = get_strategist_update()

        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
