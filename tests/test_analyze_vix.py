import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.analyze_vix_threshold import fetch_data, process_vix_signals, generate_report_content, analyze_vix
except ImportError:
    # If src is not a package, try adding src to path directly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
    from analyze_vix_threshold import fetch_data, process_vix_signals, generate_report_content, analyze_vix

class TestAnalyzeVix(unittest.TestCase):

    def setUp(self):
        # Create a sample DataFrame
        # 200 business days in 2023
        self.dates = pd.date_range(start='2023-01-01', periods=300, freq='B')
        self.df = pd.DataFrame(index=self.dates)
        self.df['^VIX'] = 20.0
        self.df['^GSPC'] = 4000.0

    def test_process_vix_signals_no_crossing(self):
        """Test that no signals are generated when VIX stays below threshold."""
        results = process_vix_signals(self.df)
        self.assertEqual(len(results), 0)

    def test_process_vix_signals_crossing(self):
        """Test a valid VIX crossing event."""
        # Create a crossing at index 10
        # Day 9: 20 (default)
        # Day 10: 25 -> Crossing! (Prev=20 <= 24, Curr=25 > 24)
        idx_cross = 10
        self.df.iloc[idx_cross, self.df.columns.get_loc('^VIX')] = 25.0

        date_cross = self.df.index[idx_cross]

        # Determine target date (approx +90 days)
        target_date = date_cross + timedelta(days=90)

        # Find index for target date
        idx_target = self.df.index.searchsorted(target_date)

        # Ensure we have enough data
        self.assertTrue(idx_target < len(self.df), "Not enough data for test case")

        # Set prices
        price_t0 = 4000.0
        price_t3m = 4400.0 # +10%

        self.df.iloc[idx_cross, self.df.columns.get_loc('^GSPC')] = price_t0
        self.df.iloc[idx_target, self.df.columns.get_loc('^GSPC')] = price_t3m

        results = process_vix_signals(self.df)

        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res['Date'], date_cross)
        self.assertEqual(res['VIX_at_Cross'], 25.0)
        self.assertAlmostEqual(res['Return_3M'], 0.10)
        self.assertEqual(res['Classification'], 'Buy')

    def test_process_vix_signals_drawdown(self):
        """Test drawdown calculation during the period."""
        idx_cross = 10
        self.df.iloc[idx_cross, self.df.columns.get_loc('^VIX')] = 25.0

        date_cross = self.df.index[idx_cross]
        target_date = date_cross + timedelta(days=90)
        idx_target = self.df.index.searchsorted(target_date)

        # Flat return
        self.df.iloc[idx_cross, self.df.columns.get_loc('^GSPC')] = 4000.0
        self.df.iloc[idx_target, self.df.columns.get_loc('^GSPC')] = 4000.0

        # Major drawdown in between
        idx_drawdown = idx_cross + 10
        self.df.iloc[idx_drawdown, self.df.columns.get_loc('^GSPC')] = 3200.0 # -20%

        results = process_vix_signals(self.df)

        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertAlmostEqual(res['Max_Drawdown_3M'], -0.20)
        self.assertIn("Major Drawdown", res['Outcome'])
        self.assertEqual(res['Classification'], 'Crash') # Drawdown < -0.15

    def test_process_vix_signals_insufficient_future_data(self):
        """Test that signals near the end of data are skipped."""
        idx_cross = len(self.df) - 5
        self.df.iloc[idx_cross, self.df.columns.get_loc('^VIX')] = 25.0
        # Prev is 20 by default

        results = process_vix_signals(self.df)
        self.assertEqual(len(results), 0)

    def test_process_vix_signals_missing_columns(self):
        """Test handling of missing columns."""
        bad_df = pd.DataFrame({'A': [1, 2, 3]})
        results = process_vix_signals(bad_df)
        self.assertEqual(results, [])

    def test_generate_report_content(self):
        """Test report generation logic."""
        results = [{
            'Date': datetime(2023, 1, 1),
            'VIX_at_Cross': 25.5,
            'SP500_Price': 4000,
            'SP500_3M_Price': 4400,
            'Return_3M': 0.10,
            'Max_Drawdown_3M': -0.05,
            'Outcome': 'Buy Signal',
            'Classification': 'Buy'
        }]

        report = generate_report_content(results)

        self.assertIn("# VIX Threshold Analysis", report)
        self.assertIn("2023-01-01", report)
        self.assertIn("25.50", report)
        self.assertIn("10.00%", report)
        self.assertIn("**Win Rate (Positive Return):** 100%", report)

    def test_generate_report_content_empty(self):
        """Test report generation with no results."""
        report = generate_report_content([])
        self.assertIn("No events found", report)

    @patch('src.analyze_vix_threshold.yf.download')
    def test_fetch_data_success(self, mock_download):
        """Test successful data fetching."""
        mock_df = pd.DataFrame()
        mock_download.return_value = mock_df

        start = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)

        result = fetch_data(start, end)

        mock_download.assert_called_once()
        self.assertIs(result, mock_df)

    @patch('src.analyze_vix_threshold.yf.download')
    def test_fetch_data_failure(self, mock_download):
        """Test data fetching failure."""
        mock_download.side_effect = Exception("Network error")

        result = fetch_data(datetime.now(), datetime.now())
        self.assertIsNone(result)

    @patch('src.analyze_vix_threshold.fetch_data')
    @patch('src.analyze_vix_threshold.process_vix_signals')
    @patch('src.analyze_vix_threshold.generate_report_content')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.makedirs')
    def test_analyze_vix_orchestration(self, mock_makedirs, mock_open, mock_gen, mock_proc, mock_fetch):
        """Test the main orchestration function."""
        # Setup mocks
        mock_fetch.return_value = pd.DataFrame()
        mock_proc.return_value = []
        mock_gen.return_value = "Report Content"

        analyze_vix()

        mock_fetch.assert_called_once()
        mock_proc.assert_called_once()
        mock_gen.assert_called_once()
        mock_makedirs.assert_called_once()
        mock_open.assert_called_with("docs/VIX_Threshold_Analysis.md", "w")
        mock_open().write.assert_called_with("Report Content")

    @patch('src.analyze_vix_threshold.fetch_data')
    def test_analyze_vix_no_data(self, mock_fetch):
        """Test orchestration stops if no data."""
        mock_fetch.return_value = None

        # Redirect stdout to suppress print
        with patch('sys.stdout', new=pd.io.common.StringIO()):
            analyze_vix()

        # Should return early and not call other functions (if we mocked them, but here checking return)
        # We can verify by patching process_vix_signals and ensuring it's not called
        with patch('src.analyze_vix_threshold.process_vix_signals') as mock_proc:
            analyze_vix()
            mock_proc.assert_not_called()

if __name__ == '__main__':
    unittest.main()
