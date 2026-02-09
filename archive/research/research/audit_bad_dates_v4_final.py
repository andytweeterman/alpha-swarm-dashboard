import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys

# ==========================================
# 1. SETUP
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
txt_path = os.path.join(script_dir, "Bad_Date_Audit_Final.txt")

# Redirect output to file
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(txt_path, "w")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self): pass

sys.stdout = Logger()

print("--- [ALPHA SWARM: BAD DATE AUDIT v4 (SMART LOOKUP)] ---")

# ==========================================
# 2. THE BAD DATES
# ==========================================
bad_dates_map = {
    "2007-08-08": "Credit Freeze (BNP)",
    "2008-09-15": "Lehman Bankruptcy",
    "2008-10-01": "2008 Crash Peak",
    "2010-05-06": "Flash Crash",
    "2011-08-03": "US Debt Downgrade",
    "2018-12-12": "Trade War / Rates",
    "2020-02-19": "COVID Start",
    "2020-03-11": "COVID Panic",
    "2022-06-08": "Inflation Shock",
    "2025-04-09": "Tariff Flop"
}

# ==========================================
# 3. THE ENGINE
# ==========================================
print("Downloading data...")
tickers = ["HYG", "IEF", "^VIX", "RSP", "SPY", "DX-Y.NYB"]
data = yf.download(tickers, start="2007-01-01", progress=False)['Close']
data.dropna(inplace=True)

df = pd.DataFrame(index=data.index)
df['Credit_Ratio'] = data["HYG"] / data["IEF"]
df['Credit_Delta'] = df['Credit_Ratio'].pct_change(10)
df['VIX'] = data["^VIX"]
df['Breadth_Ratio'] = data["RSP"] / data["SPY"]
df['Breadth_Delta'] = df['Breadth_Ratio'].pct_change(20)
df['DXY_Delta'] = data["DX-Y.NYB"].pct_change(5)

# Logic
def get_level(row):
    credit_bad = row['Credit_Delta'] < -0.015
    vol_bad = row['VIX'] > 24.0
    breadth_bad = row['Breadth_Delta'] < -0.025
    dxy_bad = row['DXY_Delta'] > 0.02
    
    if credit_bad or dxy_bad: return "EMERGENCY (Level 7)"
    elif vol_bad and breadth_bad: return "CAUTION (Level 5)"
    elif breadth_bad or vol_bad: return "WATCHLIST (Level 4)"
    else: return "NORMAL (Level 3)"

# Shift by 1 to prevent look-ahead bias
df['Morning_Signal'] = df.apply(get_level, axis=1).shift(1).fillna("NORMAL (Level 3)")

# ==========================================
# 4. THE SMART SCORECARD
# ==========================================
print("\n" + "="*85)
print(f"{'DATE':<12} | {'EVENT':<20} | {'MORNING SIGNAL':<20} | {'RESULT'}")
print("="*85)

score = 0
total = 0

for date_str, event in bad_dates_map.items():
    try:
        # SMART LOOKUP: Find the index of the date nearest to the target
        dt = pd.to_datetime(date_str)
        idx = df.index.get_indexer([dt], method='nearest')[0]
        
        # Check if the found date is reasonably close (within 3 days)
        found_date = df.index[idx]
        diff = abs((found_date - dt).days)
        
        if diff > 4:
            print(f"{date_str:<12} | {event:<20} | {'[NO DATA NEARBY]':<20} | --")
            continue
            
        signal = df.iloc[idx]['Morning_Signal']
        passed = "NORMAL" not in signal
        status = "✅ CAUGHT" if passed else "❌ MISSED"
        if passed: score += 1
        total += 1
        
        print(f"{date_str:<12} | {event:<20} | {signal:<20} | {status}")
        
    except Exception as e:
        print(f"{date_str:<12} | {event:<20} | Error: {e}")

print("="*85)
print(f"FINAL SCORE: {score}/{total}")
print("="*85)