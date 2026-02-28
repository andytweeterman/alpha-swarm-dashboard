import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyze_vix_threshold import analyze_vix

class TestAnalyzeVixThreshold(unittest.TestCase):

    def setUp(self):
        # We need to capture stdout to prevent test output clutter
        self.held_stdout = sys.stdout
        sys.stdout = io.StringIO()

    def tearDown(self):
        sys.stdout = self.held_stdout

    @patch('src.analyze_vix_threshold.yf.download')
    @patch('src.analyze_vix_threshold.os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    def test_analyze_vix_happy_path(self, mock_open, mock_makedirs, mock_download):
        # Create a mock DataFrame with MultiIndex columns, simulating yfinance output

        # Define dates
        dates = pd.date_range(start='2020-01-01', periods=100, freq='D')

        # VIX values
        vix_values = np.full(100, 20.0)
        # Cross 24 on day 10 (index 10)
        vix_values[10] = 25.0
        # Drop back down to 20
        vix_values[11:] = 20.0

        # SP500 values
        sp500_values = np.full(100, 1000.0)
        # Drop price slightly to simulate drawdown
        sp500_values[15:20] = 900.0
        # Price 90 days later (around index 100, we'll make the dataframe large enough)

        # We need a dataframe spanning at least 90 days after index 10
        dates = pd.date_range(start='2020-01-01', periods=120, freq='D')
        vix_values = np.full(120, 20.0)
        vix_values[10] = 25.0

        sp500_values = np.full(120, 1000.0)
        sp500_values[15:20] = 850.0  # -15% drawdown
        sp500_values[100] = 1100.0 # +10% return

        # Create MultiIndex
        columns = pd.MultiIndex.from_tuples([('Close', '^VIX'), ('Close', '^GSPC')])
        df = pd.DataFrame({
            ('Close', '^VIX'): vix_values,
            ('Close', '^GSPC'): sp500_values
        }, index=dates)

        mock_download.return_value = df

        # Mock open context manager
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function
        analyze_vix()

        # Assertions
        mock_download.assert_called_once()
        # The code does: os.makedirs(os.path.dirname(output_path), exist_ok=True)
        mock_makedirs.assert_called_once_with('docs', exist_ok=True)

        # Check written content
        written_content = "".join(call.args[0] for call in mock_file.write.call_args_list)
        self.assertIn("Buy Signal", written_content)
        self.assertIn("-15.00%", written_content) # Drawdown check
        self.assertIn("10.00%", written_content) # Return check

    @patch('src.analyze_vix_threshold.yf.download')
    @patch('src.analyze_vix_threshold.os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    def test_analyze_vix_no_crossings(self, mock_open, mock_makedirs, mock_download):
        dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
        vix_values = np.full(10, 20.0)
        sp500_values = np.full(10, 1000.0)

        df = pd.DataFrame({
            ('Close', '^VIX'): vix_values,
            ('Close', '^GSPC'): sp500_values
        }, index=dates)

        mock_download.return_value = df
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        analyze_vix()

        written_content = "".join(call.args[0] for call in mock_file.write.call_args_list)
        self.assertIn("No events found in the specified period.", written_content)

    @patch('src.analyze_vix_threshold.yf.download')
    @patch('src.analyze_vix_threshold.os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    def test_analyze_vix_not_enough_future_data(self, mock_open, mock_makedirs, mock_download):
        # Data where VIX crosses 24 but ends right after, so no 3-month future data
        dates = pd.date_range(start='2020-01-01', periods=20, freq='D')
        vix_values = np.full(20, 20.0)
        vix_values[10] = 25.0 # Crosses here
        sp500_values = np.full(20, 1000.0)

        df = pd.DataFrame({
            ('Close', '^VIX'): vix_values,
            ('Close', '^GSPC'): sp500_values
        }, index=dates)

        mock_download.return_value = df
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        analyze_vix()

        # It should skip the date because there is no target_date available
        # The output shouldn't have results but will still write the markdown
        written_content = "".join(call.args[0] for call in mock_file.write.call_args_list)
        self.assertIn("No events found in the specified period.", written_content)

        # Check stdout for skipping message
        output = sys.stdout.getvalue()
        self.assertIn("Skipping", output)
        self.assertIn("Not enough future data", output)

    @patch('src.analyze_vix_threshold.yf.download')
    def test_analyze_vix_download_error(self, mock_download):
        mock_download.side_effect = Exception("Mocked download error")

        analyze_vix()

        output = sys.stdout.getvalue()
        self.assertIn("Error downloading data: Mocked download error", output)

    @patch('src.analyze_vix_threshold.yf.download')
    def test_analyze_vix_missing_columns(self, mock_download):
        dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
        df = pd.DataFrame({
            ('Close', 'AAPL'): np.full(10, 100.0)
        }, index=dates)

        mock_download.return_value = df

        analyze_vix()

        output = sys.stdout.getvalue()
        self.assertIn("Error: Could not find ^VIX or ^GSPC in downloaded data.", output)

    @patch('src.analyze_vix_threshold.yf.download')
    @patch('src.analyze_vix_threshold.os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    def test_analyze_vix_flat_dataframe_fallback(self, mock_open, mock_makedirs, mock_download):
        dates = pd.date_range(start='2020-01-01', periods=120, freq='D')
        vix_values = np.full(120, 20.0)
        sp500_values = np.full(120, 1000.0)

        # Flat DataFrame without MultiIndex
        df = pd.DataFrame({
            '^VIX': vix_values,
            '^GSPC': sp500_values
        }, index=dates)

        mock_download.return_value = df
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        analyze_vix()

        # It should process correctly and write markdown
        written_content = "".join(call.args[0] for call in mock_file.write.call_args_list)
        self.assertIn("No events found in the specified period.", written_content)

if __name__ == '__main__':
    unittest.main()
