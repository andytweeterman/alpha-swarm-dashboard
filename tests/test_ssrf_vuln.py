import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock streamlit before import
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st

# Add repo root to path
sys.path.append(os.getcwd())

# Mock yfinance to avoid network calls
sys.modules['yfinance'] = MagicMock()

# Import logic instead of app
from logic import get_strategist_update

class TestSSRFVuln(unittest.TestCase):
    @patch('logic.pd.read_csv')
    @patch('logic.os.environ.get')
    def test_ssrf_mitigation_http(self, mock_env_get, mock_read_csv):
        mock_env_get.return_value = "http://example.com/data.csv"
        mock_read_csv.return_value = "mock_data"

        result = get_strategist_update()

        mock_read_csv.assert_called_once_with("http://example.com/data.csv")
        self.assertEqual(result, "mock_data")

    @patch('logic.pd.read_csv')
    @patch('logic.os.environ.get')
    def test_ssrf_mitigation_https(self, mock_env_get, mock_read_csv):
        mock_env_get.return_value = "https://example.com/data.csv"
        mock_read_csv.return_value = "mock_data"

        result = get_strategist_update()

        mock_read_csv.assert_called_once_with("https://example.com/data.csv")
        self.assertEqual(result, "mock_data")

    @patch('logic.pd.read_csv')
    @patch('logic.os.environ.get')
    def test_ssrf_mitigation_file_scheme(self, mock_env_get, mock_read_csv):
        mock_env_get.return_value = "file:///etc/passwd"

        result = get_strategist_update()

        mock_read_csv.assert_not_called()
        self.assertIsNone(result)

    @patch('logic.pd.read_csv')
    @patch('logic.os.environ.get')
    def test_ssrf_mitigation_ftp_scheme(self, mock_env_get, mock_read_csv):
        mock_env_get.return_value = "ftp://example.com/data.csv"

        result = get_strategist_update()

        mock_read_csv.assert_not_called()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
