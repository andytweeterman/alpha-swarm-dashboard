import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys
import io

# Add the root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import get_strategist_update

class TestSecurityFix(unittest.TestCase):

    @patch('logic.st.secrets', {})
    @patch.dict(os.environ, {"STRATEGIST_SHEET_URL": "http://example.com/sheet.csv"})
    @patch('logic.requests.get')
    def test_secure_request_success(self, mock_get):
        """Test that a valid, small CSV is processed correctly."""
        # Mock a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': '100'}
        mock_csv_content = b"col1,col2\n1,2"
        mock_response.iter_content.return_value = [mock_csv_content]

        # Configure context manager
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None

        mock_get.return_value = mock_response

        # Call the function
        df = get_strategist_update()

        # Verify requests.get was called with timeout and stream=True
        mock_get.assert_called_with("http://example.com/sheet.csv", timeout=10, stream=True)

        # Verify the DataFrame is returned correctly
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['col1'], 1)

    @patch('logic.st.secrets', {})
    @patch.dict(os.environ, {"STRATEGIST_SHEET_URL": "http://example.com/sheet.csv"})
    @patch('logic.requests.get')
    def test_request_timeout(self, mock_get):
        """Test that a timeout is handled gracefully."""
        # Mock a timeout exception
        import requests
        mock_get.side_effect = requests.Timeout

        # Call the function
        df = get_strategist_update()

        # Verify it returns None (or handles it gracefully)
        self.assertIsNone(df)

    @patch('logic.st.secrets', {})
    @patch.dict(os.environ, {"STRATEGIST_SHEET_URL": "http://example.com/large.csv"})
    @patch('logic.requests.get')
    def test_large_file_streaming(self, mock_get):
        """Test that a file exceeding the size limit is rejected during streaming."""
        # Mock a response that streams too much data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}

        # Configure context manager
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None

        # Create a generator that yields chunks until it exceeds the limit (5MB)
        def large_content_generator():
            chunk = b"a" * 1024 * 1024  # 1MB chunk
            for _ in range(6):  # 6MB total
                yield chunk

        mock_response.iter_content.return_value = large_content_generator()
        mock_get.return_value = mock_response

        # Call the function
        df = get_strategist_update()

        # Verify it returns None because of size limit
        self.assertIsNone(df)

    @patch('logic.st.secrets', {})
    @patch.dict(os.environ, {"STRATEGIST_SHEET_URL": "http://example.com/large_header.csv"})
    @patch('logic.requests.get')
    def test_large_content_length_header(self, mock_get):
        """Test that a file with a large Content-Length header is rejected immediately."""
        # Mock a response with a large Content-Length header
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': str(6 * 1024 * 1024)} # 6MB

        # Configure context manager
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None

        mock_get.return_value = mock_response

        # Call the function
        df = get_strategist_update()

        # Verify it returns None
        self.assertIsNone(df)

if __name__ == '__main__':
    unittest.main()
