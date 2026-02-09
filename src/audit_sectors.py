import yfinance as yf
import pandas as pd
import time

# --- INPUT: DAD'S LIST (Add more here) ---
# For now, I put in a mix of common ETFs and Stocks to test.
tickers = [
    "XLE", "XOM", "CVX", "COP", "SLB",  # Energy
    "XLK", "AAPL", "MSFT", "NVDA",      # Tech
    "XLU", "NEE", "DUK", "SO",          # Utilities
    "XLV", "JNJ", "PFE", "MRK",         # Healthcare
    "URA", "CCJ", "DNN",                # Uranium (for his reviewer!)
    "SPY", "QQQ", "IWM"                 # Broad Market
]

print(f"🔍 Auditing {len(tickers)} tickers for GICS Sector coverage...")
print("-" * 50)

sector_counts = {}
missing_data = []

for ticker in tickers:
    try:
        # Fetch info from Yahoo
        info = yf.Ticker(ticker).info
        
        # Get Sector (or 'ETF' if it's a fund)
        sector = info.get('sector', 'Unknown/ETF')
        
        # Count it
        if sector in sector_counts:
            sector_counts[sector] += 1
        else:
            sector_counts[sector] = 1
            
        print(f"✅ {ticker}: {sector}")
        
    except Exception as e:
        print(f"❌ {ticker}: Failed ({e})")
        missing_data.append(ticker)
    
    # Sleep to be polite to Yahoo API
    time.sleep(0.2)

print("-" * 50)
print("📊 FINAL SECTOR BREAKDOWN")
print("-" * 50)

# Convert to DataFrame for nice display
df = pd.DataFrame(list(sector_counts.items()), columns=['Sector', 'Count'])
df = df.sort_values('Count', ascending=False)
print(df.to_string(index=False))

if missing_data:
    print(f"\n⚠️ Could not identify: {missing_data}")