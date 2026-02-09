import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_TXT = "Bad_Date_Audit_Report.txt"
OUTPUT_CSV = "audit_data_full.csv"

# Redirect output to both screen AND file
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(OUTPUT_TXT, "w")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        pass    

# Start Logging
sys.stdout = Logger()

print("--- [ALPHA SWARM: BAD DATE AUDIT v2] ---")

# ==========================================
# 1. THE "BAD DATE" LIST (From Dad's Email)
# ==========================================
# I added the "Likely Cause" based on his email for better reporting
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
    "2025-04-09": "Tariff Flop (Projected)"
}

# ==========================================
# 2. REBUILD THE ENGINE
# ==========================================
print("Downloading 18 years of data (HYG, IEF, VIX, DXY)...")

tickers = ["HYG", "IEF", "^VIX", "RSP", "SPY", "DX-Y.NYB"]
try:
    data = yf.download(tickers, start="2007-01-01", progress=False)['Close']
    data.dropna(inplace=True)
except Exception as e:
    print(f"[ERROR] Download failed: {e}")
    sys.exit()

df = pd.DataFrame(index=data.index)

# Indicators
df['Credit_Ratio'] = data["HYG"] / data["IEF"]
df['Credit_Delta'] = df['Credit_Ratio'].pct_change(10)
df['VIX'] = data["^VIX"]
df['Breadth_Ratio'] = data["RSP"] / data["SPY"]
df['Breadth_Delta'] = df['Breadth_Ratio'].pct_change(20)
df['DXY_Delta'] = data["DX-Y.NYB"].pct_change(5) # 5-Day Dollar Spike

# Thresholds
CREDIT_TRIG = -0.015
VIX_PANIC = 24.0
BREADTH_TRIG = -0.025
DXY_SPIKE = 0.02

# Logic
def get_level(row):
    credit_bad = row['Credit_Delta'] < CREDIT_TRIG
    vol_bad = row['VIX'] > VIX_PANIC
    breadth_bad = row['Breadth_Delta'] < BREADTH_TRIG
    dxy_bad = row['DXY_Delta'] > DXY_SPIKE
    
    if credit_bad or dxy_bad: return "EMERGENCY (Level 7)"
    elif vol_bad and breadth_bad: return "CAUTION (Level 5)"
    elif breadth_bad: return "WATCHLIST (Level 4)"
    elif vol_bad: return "VOLATILE (Level 4)" # New check for just VIX
    else: return "NORMAL (Level 3)"

df['Signal_At_Close'] = df.apply(lambda row: get_level(row), axis=1)

# CRITICAL: Shift by 1 day to simulate "Morning Of" knowledge
df['Morning_Signal'] = df['Signal_At_Close'].shift(1)
df['Morning_Signal'] = df['Morning_Signal'].fillna("NORMAL (Level 3)")

# ==========================================
# 3. THE SCORECARD
# ==========================================
print("\n" + "="*85)
print(f"{'DATE':<12} | {'EVENT':<20} | {'MORNING SIGNAL':<20} | {'RESULT'}")
print("="*85)

score = 0
total = 0

for date_str, event in bad_dates_map.items():
    try:
        dt = pd.to_datetime(date_str)
        # Find closest trading day
        idx = df.index.get_indexer([dt], method='nearest')[0]
        actual_date = df.index[idx]
        
        signal = df.iloc[idx]['Morning_Signal']
        
        # Grading
        passed = "NORMAL" not in signal
        status = "✅ CAUGHT" if passed else "❌ MISSED"
        if passed: score += 1
        total += 1
        
        print(f"{date_str:<12} | {event:<20} | {signal:<20} | {status}")
        
    except:
        print(f"{date_str:<12} | {event:<20} | {'[DATA MISSING]':<20} | --")

print("="*85)
print(f"FINAL SCORE: {score}/{total} Crises Identified Early")
print("="*85)

# Save the raw data too
df.to_csv(OUTPUT_CSV)
print(f"\n[SUCCESS] Report saved to: {OUTPUT_TXT}")
print(f"[SUCCESS] Full Data saved to: {OUTPUT_CSV}")