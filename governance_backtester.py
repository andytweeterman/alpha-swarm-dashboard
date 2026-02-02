import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys

print("--- [ALPHA SWARM: HISTORICAL BACKTESTER] ---")
print("Downloading 17 years of macro data (HYG, IEF, VIX)...")

# ==========================================
# 1. CONFIGURATION & LOGIC
# ==========================================
# Tickers
CREDIT_RISKY = "HYG"    # High Yield
CREDIT_SAFE = "IEF"     # Treasuries
VOL_INDEX = "^VIX"      # Volatility

# Thresholds (From Dad's Research + Your Logic)
CREDIT_TRIGGER = -0.015  # -1.5% drop in Credit Ratio over 10 days
VIX_PANIC = 24.0         # Structural Fear Level

# ==========================================
# 2. FETCH DATA (2007 - Present)
# ==========================================
try:
    tickers = [CREDIT_RISKY, CREDIT_SAFE, VOL_INDEX]
    # Download data from 2007-01-01 to Today
    data = yf.download(tickers, start="2007-01-01", progress=True)['Close']
    
    # Drop rows where any data is missing (common in early years or holidays)
    data.dropna(inplace=True)
    print(f"[SUCCESS] Downloaded {len(data)} trading days.")

except Exception as e:
    print(f"[ERROR] Data fetch failed: {e}")
    sys.exit()

# ==========================================
# 3. CALCULATE INDICATORS
# ==========================================
print("Applying Avalanche Logic to history...")

df = pd.DataFrame(index=data.index)

# A. Credit Physics
# Ratio of Junk vs. Safe. If this falls, liquidity is drying up.
df['Credit_Ratio'] = data[CREDIT_RISKY] / data[CREDIT_SAFE]
# 10-Day Rate of Change (The "Sudden Move" Detector)
df['Credit_Delta_10d'] = df['Credit_Ratio'].pct_change(10)

# B. Volatility Physics
df['VIX'] = data[VOL_INDEX]

# ==========================================
# 4. DETERMINE GOVERNANCE LEVELS
# ==========================================
def determine_level(row):
    # Logic from avalanche_logic_v2.py
    
    # 1. Check Triggers
    credit_broken = row['Credit_Delta_10d'] < CREDIT_TRIGGER
    vol_broken = row['VIX'] > VIX_PANIC
    
    # 2. Assign Hierarchy
    if credit_broken and vol_broken:
        return 7, "EMERGENCY" # Both triggers fired
    elif credit_broken:
        return 5, "CAUTION"   # Primary trigger fired
    elif vol_broken:
        return 4, "WATCHLIST" # Secondary trigger fired
    else:
        return 3, "NORMAL OPS" # All clear

# Apply logic row by row
df[['Gov_Level', 'Gov_Name']] = df.apply(
    lambda row: pd.Series(determine_level(row)), axis=1
)

# ==========================================
# 5. STATISTICS & SAVE
# ==========================================
# Count how many days spent in each level
summary = df['Gov_Name'].value_counts()
print("\n--- BACKTEST SUMMARY (Days spent in each mode) ---")
print(summary)

# Filter for the "Bad Dates" Dad mentioned (Just to check a few)
# 2008 Crash Peak: Oct 2008
print("\n--- SPOT CHECK: 2008 FINANCIAL CRISIS ---")
print(df['2008-09-15':'2008-10-15'][['Gov_Level', 'Gov_Name', 'VIX']].head(10))

# 2020 Covid Crash: March 2020
print("\n--- SPOT CHECK: COVID CRASH 2020 ---")
print(df['2020-02-20':'2020-03-10'][['Gov_Level', 'Gov_Name', 'VIX']].head(10))

# Save to CSV
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "governance_history.csv")
df.to_csv(output_file)

print("\n" + "="*60)
print(f"[SUCCESS] Full history saved to: {output_file}")
print("Send this CSV to Dad to overlay on his portfolio performance.")
print("="*60)

input("Press ENTER to exit...")