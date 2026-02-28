import sys
import unittest
from unittest.mock import MagicMock, patch
import os
import importlib

# Add repo root to path to import src.audit_sectors
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestAuditSectors(unittest.TestCase):

    def setUp(self):
        # We need to mock sys.modules for yfinance and pandas before importing audit_sectors
        self.mock_yf = MagicMock()
        self.mock_pd = MagicMock()

        # Patch sys.modules safely
        self.sys_modules_patcher = patch.dict(
            'sys.modules',
            {'yfinance': self.mock_yf, 'pandas': self.mock_pd}
        )
        self.sys_modules_patcher.start()

        # Now import the module or reload it if already imported
        import src.audit_sectors as audit_sectors
        importlib.reload(audit_sectors)
        self.audit_sectors = audit_sectors

        # Setup the mock ticker and info property
        self.mock_ticker_instance = MagicMock()
        self.mock_yf.Ticker.return_value = self.mock_ticker_instance

    def tearDown(self):
        # Stop the patcher to clean up sys.modules
        self.sys_modules_patcher.stop()

    def test_fetch_sector_info_success_with_sector(self):
        # Setup mock return value for info dictionary using a normal dictionary.
        # MagicMock's get method handles dictionary-like access if configured correctly,
        # but here we can just configure the mock to return the dict for .info
        # and we don't even need .get to be mocked if we pass a real dict
        # wait, if info is a dict, we just assign a dict:
        self.mock_ticker_instance.info = {'sector': 'Technology'}

        # Call function
        ticker, sector, error = self.audit_sectors.fetch_sector_info('AAPL')

        # Assertions
        self.assertEqual(ticker, 'AAPL')
        self.assertEqual(sector, 'Technology')
        self.assertIsNone(error)
        self.mock_yf.Ticker.assert_called_once_with('AAPL')

    def test_fetch_sector_info_success_without_sector(self):
        # Setup mock return value for info dictionary missing 'sector' (e.g. ETF)
        self.mock_ticker_instance.info = {}

        # Call function
        ticker, sector, error = self.audit_sectors.fetch_sector_info('SPY')

        # Assertions
        self.assertEqual(ticker, 'SPY')
        self.assertEqual(sector, 'Unknown/ETF')
        self.assertIsNone(error)
        self.mock_yf.Ticker.assert_called_once_with('SPY')

    def test_fetch_sector_info_error(self):
        # Setup mock to raise Exception when Ticker is called
        self.mock_yf.Ticker.side_effect = Exception("API Error")

        # Call function
        ticker, sector, error = self.audit_sectors.fetch_sector_info('INVALID')

        # Assertions
        self.assertEqual(ticker, 'INVALID')
        self.assertIsNone(sector)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "API Error")
        self.mock_yf.Ticker.assert_called_once_with('INVALID')

if __name__ == '__main__':
    unittest.main()
