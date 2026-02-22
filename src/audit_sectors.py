import yfinance as yf
import pandas as pd
import concurrent.futures

# --- INPUT: DAD'S LIST (Add more here) ---
# For now, I put in a mix of common ETFs and Stocks to test.
tickers = [
    "XLE", "XOM", "CVX", "COP", "SLB",  # Energy
    "XLK", "AAPL", "MSFT", "NVDA",      # Tech
    "XLU", "NEE", "DUK", "SO",          # Utilities
    "XLV", "JNJ", "PFE", "MRK",         # Healthcare
    "XLF", "JPM", "BAC",                # Financials
    "XLY", "AMZN", "TSLA",              # Consumer Discretionary
    "XLP", "PG", "KO",                  # Consumer Staples
    "XLI", "CAT", "GE",                 # Industrials
    "XLB", "LIN",                       # Materials
    "XLRE", "PLD",                      # Real Estate
    "XLC", "GOOGL", "META",             # Communication Services
    "GLD", "NEM",                       # Gold
    "URA", "CCJ", "DNN",                # Uranium (for his reviewer!)
    "SPY", "QQQ", "IWM"                 # Broad Market
]

print(f"🔍 Auditing {len(tickers)} tickers for GICS Sector coverage...")
print("-" * 50)

sector_counts = {}
missing_data = []

def fetch_sector_info(ticker):
    """Fetches sector info for a single ticker."""
    try:
        # Fetch info from Yahoo
        info = yf.Ticker(ticker).info
        
        # Get Sector (or 'ETF' if it's a fund)
        sector = info.get('sector', 'Unknown/ETF')
        return ticker, sector, None
    except Exception as e:
        return ticker, None, e

# Use ThreadPoolExecutor for concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Submit all tasks
    future_to_ticker = {executor.submit(fetch_sector_info, ticker): ticker for ticker in tickers}
    
    # Process as they complete
    for future in concurrent.futures.as_completed(future_to_ticker):
        ticker, sector, error = future.result()

        if error:
            print(f"❌ {ticker}: Failed ({error})")
            missing_data.append(ticker)
        else:
            # Count it
            if sector in sector_counts:
                sector_counts[sector] += 1
            else:
                sector_counts[sector] = 1

            print(f"✅ {ticker}: {sector}")

print("-" * 50)
print("📊 FINAL SECTOR BREAKDOWN")
print("-" * 50)

# Convert to DataFrame for nice display
df = pd.DataFrame(list(sector_counts.items()), columns=['Sector', 'Count'])
df = df.sort_values('Count', ascending=False)
print(df.to_string(index=False))

if missing_data:
    print(f"\n⚠️ Could not identify: {missing_data}")
