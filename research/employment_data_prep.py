import pandas_datareader.data as web
import datetime
import pandas as pd

# Note: This script requires pandas-datareader.
# As of early 2026, pandas-datareader 0.10.0 may have compatibility issues with pandas >= 3.0.0.
# It is recommended to use pandas < 2.2.0 (e.g., pandas 2.1.4) if you encounter import errors.

def fetch_employment_data():
    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime.now()

    # FRED Series IDs
    # Non-Farm Payrolls (Monthly): PAYEMS
    # US Unemployment Rate (Monthly): UNRATE
    # Initial Jobless Claims (Weekly): ICSA

    series_ids = ['PAYEMS', 'UNRATE', 'ICSA']

    print(f"Fetching data for series: {series_ids} from FRED...")

    try:
        df = web.DataReader(series_ids, 'fred', start, end)
        print("\nData fetched successfully!")
        print("\nHead:")
        print(df.head())
        print("\nTail:")
        print(df.tail())

        # Verify columns exist
        expected_columns = ['PAYEMS', 'UNRATE', 'ICSA']
        if all(col in df.columns for col in expected_columns):
            print("\nAll expected columns are present.")
        else:
            print("\nWARNING: Some columns are missing.")
            print(f"Found: {df.columns.tolist()}")

        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    fetch_employment_data()
