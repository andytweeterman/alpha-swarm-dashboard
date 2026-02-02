import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys

print("--- [ALPHA SWARM: HISTORICAL BACKTESTER V2 (With Breadth)] ---")
print("Downloading 17 years of macro data (HYG, IEF, VIX, RSP, SPY)...")

# ==========================================
# 1. CONFIGURATION & LOGIC
# ==========================================
# Tickers
CREDIT_RISKY = "HYG"    # High Yield
CREDIT_SAFE = "IEF"     # Treasuries
VOL_INDEX = "^VIX"      # Volatility
BREADTH_EQ = "RSP"      # S&P 500 Equal Weight (The Soldiers)
BREADTH_MKT = "SPY"     # S&P 500 Market Weight (The Generals)

# Thresholds
CREDIT_TRIGGER = -0.015  # -1.5% Credit Ratio drop in 10 days
VIX_PANIC = 24.0         # VIX > 24
BREADTH_TRIGGER = -0.025 # RSP underperforms SPY by 2.5% in 20 days (Divergence)

# ==========================================
# 2. FETCH DATA (2007 - Present)
# ==========================================
try:
    tickers = [CREDIT_RISKY, CREDIT_SAFE, VOL_INDEX, BREADTH_EQ, BREADTH_MKT]
    # Download data from 2007-01-01 to Today
    data = yf.download(tickers, start="2007-01-01", progress=True)['Close']
    
    # Drop rows where any data is missing
    data.dropna(inplace=True)
    print(f"[SUCCESS] Downloaded {len(data)} trading days.")

except Exception as e:
    print(f"[ERROR] Data fetch failed: {e}")
    sys.exit()

# ==========================================
# 3. CALCULATE INDICATORS
# ==========================================
print("Applying Avalanche Logic (Credit + Vol + Breadth)...")

df = pd.DataFrame(index=data.index)

# A. Credit Physics (The Primary Trigger)
df['Credit_Ratio'] = data[CREDIT_RISKY] / data[CREDIT_SAFE]
df['Credit_Delta_10d'] = df['Credit_Ratio'].pct_change(10)

# B. Volatility Physics
df['VIX'] = data[VOL_INDEX]

# C. Breadth Physics (The New Check)
# If Ratio goes DOWN, it means Equal Weight (Soldiers) is losing to Market Weight (Generals)
df['Breadth_Ratio'] = data[BREADTH_EQ] / data[BREADTH_MKT]
# 20-Day Rate of Change (1 Month Trend)
df['Breadth_Delta_20d'] = df['Breadth_Ratio'].pct_change(20)

# ==========================================
# 4. DETERMINE GOVERNANCE LEVELS
# ==========================================
def determine_level(row):
    # 1. Check Triggers
    credit_broken = row['Credit_Delta_10d'] < CREDIT_TRIGGER
    vol_broken = row['VIX'] > VIX_PANIC
    breadth_broken = row['Breadth_Delta_20d'] < BREADTH_TRIGGER
    
    # 2. Assign Hierarchy (Credit is King)
    
    # --- TIER 1: EMERGENCY (Multiple Systems Failure) ---
    # If Credit breaks AND (Vol OR Breadth breaks)
    if credit_broken and (vol_broken or breadth_broken):
        return 7, "EMERGENCY"
    
    # --- TIER 2: CAUTION (Primary System Failure) ---
    # If Credit breaks alone
    elif credit_broken:
        return 5, "CAUTION"
    
    # --- TIER 3: WATCHLIST (Secondary System Failure) ---
    # Credit is fine, but Vol is high OR Breadth is thinning
    elif vol_broken or breadth_broken:
        return 4, "WATCHLIST"
    
    # --- TIER 4: NORMAL ---
    else:
        return 3, "NORMAL OPS"

# Apply logic
df[['Gov_Level', 'Gov_Name']] = df.apply(
    lambda row: pd.Series(determine_level(row)), axis=1
)

# ==========================================
# 5. STATISTICS & SAVE
# ==========================================
summary = df['Gov_Name'].value_counts()
print("\n--- BACKTEST SUMMARY (Days spent in each mode) ---")
print(summary)

# SPOT CHECK: 2020 Covid Crash (Breadth usually fails first)
print("\n--- SPOT CHECK: COVID CRASH 2020 ---")
print(df['2020-02-15':'2020-03-15'][['Gov_Level', 'Gov_Name', 'VIX', 'Breadth_Delta_20d']].head(10))

# Save to CSV
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "governance_history_v2.csv")
df.to_csv(output_file)

print("\n" + "="*60)
print(f"[SUCCESS] Updated history saved to: {output_file}")
print("Includes new columns: 'Breadth_Ratio' and 'Breadth_Delta_20d'")
print("="*60)

input("Press ENTER to exit...")