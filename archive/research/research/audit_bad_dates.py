import yfinance as yf
import pandas as pd
import numpy as np

print("--- [ALPHA SWARM: BAD DATE AUDIT] ---")

# ==========================================
# 1. THE "BAD DATE" LIST (From Dad's Email)
# ==========================================
bad_dates_str = [
    "2007-08-08", "2008-09-03", "2008-09-15", "2008-10-01", # 2008 Crisis
    "2010-05-06", "2011-08-03",                             # Flash Crash / Debt Crisis
    "2018-10-03", "2018-12-12",                             # Trade War
    "2020-02-19", "2020-03-11",                             # COVID
    "2022-06-08",                                           # Inflation Shock
    "2025-04-09"                                            # The Tariff Flop
]

# ==========================================
# 2. REBUILD THE ENGINE (Quick Calculation)
# ==========================================
print("Re-calculating historical risk levels...")

tickers = ["HYG", "IEF", "^VIX", "RSP", "SPY", "DX-Y.NYB"] # Added Dollar (DXY)
data = yf.download(tickers, start="2007-01-01", progress=False)['Close']
data.dropna(inplace=True)

df = pd.DataFrame(index=data.index)

# A. Indicators
df['Credit_Ratio'] = data["HYG"] / data["IEF"]
df['Credit_Delta'] = df['Credit_Ratio'].pct_change(10)
df['VIX'] = data["^VIX"]
df['Breadth_Ratio'] = data["RSP"] / data["SPY"]
df['Breadth_Delta'] = df['Breadth_Ratio'].pct_change(20)
df['DXY_Delta'] = data["DX-Y.NYB"].pct_change(5) # 5-Day Dollar Spike

# B. Thresholds
CREDIT_TRIG = -0.015
VIX_PANIC = 24.0
BREADTH_TRIG = -0.025
DXY_SPIKE = 0.02

# C. Logic (The "Honda" Engine)
def get_level(row):
    # Triggers
    credit_bad = row['Credit_Delta'] < CREDIT_TRIG
    vol_bad = row['VIX'] > VIX_PANIC
    breadth_bad = row['Breadth_Delta'] < BREADTH_TRIG
    dxy_bad = row['DXY_Delta'] > DXY_SPIKE
    
    # Hierarchy
    if credit_bad or dxy_bad: # Structural or Policy Shock
        return 7, "EMERGENCY"
    elif vol_bad and breadth_bad: # Market internals failing
        return 5, "CAUTION"
    elif breadth_bad: # Just breadth (Early Warning)
        return 4, "WATCHLIST"
    else:
        return 3, "NORMAL"

# Calculate Level
df[['Level', 'Label']] = df.apply(lambda row: pd.Series(get_level(row)), axis=1)

# D. THE LAGGED SIGNAL (What we knew that morning)
df['Morning_Signal'] = df['Label'].shift(1) # Shift 1 day to avoid look-ahead bias

# ==========================================
# 3. THE SCORECARD
# ==========================================
print("\n" + "="*60)
print(f"{'BAD DATE':<15} | {'OUR SIGNAL (MORNING OF)':<20} | {'RESULT'}")
print("="*60)

score = 0
total = 0

for date_str in bad_dates_str:
    try:
        dt = pd.to_datetime(date_str)
        # Find closest trading day if exact date missing
        idx = df.index.get_indexer([dt], method='nearest')[0]
        actual_date = df.index[idx]
        
        signal = df.iloc[idx]['Morning_Signal']
        
        # Grading: Did we flag it?
        # Pass if NOT "NORMAL"
        status = "✅ CAUGHT" if signal != "NORMAL" else "❌ MISSED"
        if signal != "NORMAL": score += 1
        total += 1
        
        print(f"{date_str:<15} | {signal:<20} | {status}")
        
    except:
        print(f"{date_str:<15} | {'[DATA MISSING]':<20} | --")

print("="*60)
print(f"FINAL SCORE: {score}/{total} Crises Identified Early")
print("="*60)