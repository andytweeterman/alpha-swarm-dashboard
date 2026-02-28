import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys

print("--- [ALPHA SWARM: HISTORICAL BACKTESTER V3 (NO LOOK-AHEAD BIAS)] ---")

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Tickers
CREDIT_RISKY = "HYG"    # High Yield
CREDIT_SAFE = "IEF"     # Treasuries
VOL_INDEX = "^VIX"      # Volatility
BREADTH_EQ = "RSP"      # S&P 500 Equal Weight
BREADTH_MKT = "SPY"     # S&P 500 Market Weight

# Thresholds
CREDIT_TRIGGER = -0.015  # -1.5% Credit Ratio drop in 10 days
VIX_PANIC = 24.0         # VIX > 24
BREADTH_TRIGGER = -0.025 # RSP underperforms SPY by 2.5% in 20 days

# ==========================================
# 2. FETCH DATA (2007 - Present)
# ==========================================
try:
    print("Downloading data...")
    tickers = [CREDIT_RISKY, CREDIT_SAFE, VOL_INDEX, BREADTH_EQ, BREADTH_MKT]
    data = yf.download(tickers, start="2007-01-01", progress=False)['Close']
    data.dropna(inplace=True)
    print(f"[SUCCESS] Downloaded {len(data)} trading days.")

except Exception as e:
    print(f"[ERROR] Data fetch failed: {e}")
    sys.exit()

# ==========================================
# 3. CALCULATE INDICATORS (AT CLOSE)
# ==========================================
print("Calculating Physics...")
df = pd.DataFrame(index=data.index)

# Credit Physics
df['Credit_Ratio'] = data[CREDIT_RISKY] / data[CREDIT_SAFE]
df['Credit_Delta_10d'] = df['Credit_Ratio'].pct_change(10)

# Volatility Physics
df['VIX'] = data[VOL_INDEX]

# Breadth Physics
df['Breadth_Ratio'] = data[BREADTH_EQ] / data[BREADTH_MKT]
df['Breadth_Delta_20d'] = df['Breadth_Ratio'].pct_change(20)

# ==========================================
# 4. DETERMINE GOVERNANCE LEVELS
# ==========================================
def determine_level(row):
    # Check Triggers (Based on Closing Data)
    credit_broken = row['Credit_Delta_10d'] < CREDIT_TRIGGER
    vol_broken = row['VIX'] > VIX_PANIC
    breadth_broken = row['Breadth_Delta_20d'] < BREADTH_TRIGGER
    
    # Hierarchy
    if credit_broken and (vol_broken or breadth_broken):
        return 7
    elif credit_broken:
        return 5
    elif vol_broken or breadth_broken:
        return 4
    else:
        return 3

# Apply logic to get "Closing Level"
df['Gov_Level_At_Close'] = df.apply(determine_level, axis=1)

# ==========================================
# 5. THE "SAFE" SIGNAL (LAGGED)
# ==========================================
# CRITICAL FIX: To trade at the OPEN of Day T, we must use the signal from Day T-1.
# We shift the column down by 1 row to ensure no look-ahead bias.
df['Signal_For_Next_Open'] = df['Gov_Level_At_Close'].shift(1)

# Fill the first day (NaN) with Normal Ops (3)
df['Signal_For_Next_Open'] = df['Signal_For_Next_Open'].fillna(3).astype(int)

# ==========================================
# 6. SAVE
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "governance_history_v3_safe.csv")
df.to_csv(output_file)

print("\n" + "="*60)
print(f"[SUCCESS] Safe History Saved: {output_file}")
print("-" * 60)
print("IMPORTANT FOR BACKTESTING:")
print("1. 'Gov_Level_At_Close'     = What happened TODAY (Do not use for Open trades).")
print("2. 'Signal_For_Next_Open'   = What you knew this MORNING (Use this!).")
print("="*60)

# Spot check to verify Lag
print("\n--- LAG CHECK (Verify Shift) ---")
print(df[['Gov_Level_At_Close', 'Signal_For_Next_Open']].tail(5))

input("Press ENTER to exit...")