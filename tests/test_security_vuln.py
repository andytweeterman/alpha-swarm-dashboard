
import os
import pandas as pd
import unittest
from unittest.mock import patch, MagicMock
import sys
import shutil

# Mock streamlit before importing app
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st

# Configure st.columns to return a list of mocks
def side_effect_columns(spec, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, list):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

mock_st.columns.side_effect = side_effect_columns
mock_st.tabs.side_effect = lambda tabs: [MagicMock() for _ in tabs]
mock_st.cache_data = lambda **kwargs: lambda func: func
mock_st.set_page_config = MagicMock()
mock_st.sidebar = MagicMock()
mock_st.toggle.return_value = False
mock_st.sidebar.toggle.return_value = False
mock_st.session_state = {}

# Import the function to test
sys.path.append(os.getcwd())

# Mock yfinance to avoid network calls
sys.modules['yfinance'] = MagicMock()

import app

class TestSecurityFix(unittest.TestCase):
    def setUp(self):
        # Create a dummy malicious file in root
        self.malicious_file = "malicious_GSPC_file.csv"
        with open(self.malicious_file, "w") as f:
            f.write("Date,Tstk_Adj,FP1,FP3,FP6\n2023-01-01,666,0.1,0.2,0.3")

        # Ensure data directory exists
        if not os.path.exists("data"):
            os.makedirs("data")

        # Create a valid file in the expected location
        self.valid_file = "data/strategist_forecast.csv"
        with open(self.valid_file, "w") as f:
            f.write("Date,Tstk_Adj,FP1,FP3,FP6\n2023-01-01,999,0.1,0.2,0.3")

    def tearDown(self):
        if os.path.exists(self.malicious_file):
            os.remove(self.malicious_file)
        if os.path.exists(self.valid_file):
            os.remove(self.valid_file)

    def test_malicious_file_ignored(self):
        # Temporarily remove valid file if it exists to test that malicious one isn't picked up as fallback
        if os.path.exists(self.valid_file):
            os.remove(self.valid_file)

        df = app.load_strategist_data()

        # Should return None because valid file is missing and malicious file should be ignored
        self.assertIsNone(df, "Should return None when only malicious file exists in root")

        # Restore valid file for other tests (though setUp/tearDown handles it)
        with open(self.valid_file, "w") as f:
             f.write("Date,Tstk_Adj,FP1,FP3,FP6\n2023-01-01,999,0.1,0.2,0.3")

    def test_valid_file_loaded(self):
        df = app.load_strategist_data()

        self.assertIsNotNone(df, "Should load data from data/strategist_forecast.csv")
        self.assertEqual(len(df), 1)
        # Check specific value to ensure it loaded the correct file
        self.assertEqual(df.iloc[0]['Tstk_Adj'], 999)

if __name__ == '__main__':
    unittest.main()
