import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os  # Add this at the very top of your file with other imports

# ==========================================
# CONFIGURATION
# ==========================================
# Tickers for the "Snowpack" Layers
# Layer 1: Credit (Junk Bonds vs 7-10yr Treasuries)
CREDIT_RISKY = "HYG"
CREDIT_SAFE = "IEF"

# Layer 2: Volatility (Spot VIX)
# Note: Real VIX Term structure requires futures data, using VIX > 20 as proxy for now
VOL_INDEX = "^VIX"

# Layer 3: Currency (US Dollar Index)
CURRENCY = "DX-Y.NYB" 

print("--- [SYSTEM START] RUNNING AVALANCHE DIAGNOSTICS ---")

# ==========================================
# 1. FETCH MACRO DATA (Last 30 Days)
# ==========================================
def fetch_data():
    tickers = [CREDIT_RISKY, CREDIT_SAFE, VOL_INDEX, CURRENCY]
    print(f"Fetching data for: {tickers}...")
    try:
        data = yf.download(tickers, period="1mo", progress=False)['Close']
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

df = fetch_data()

if df.empty:
    print("CRITICAL ERROR: No data fetched. Check internet connection.")
    exit()

# ==========================================
# 2. RUN THE CHECKS (The "Snowpack" Analysis)
# ==========================================
flags = []
report_lines = []

# --- CHECK 1: CREDIT STRESS (Liquidity) ---
# Logic: If HYG is underperforming IEF by > 1.5% in the last 10 days, credit is cracking.
hyg = df[CREDIT_RISKY]
ief = df[CREDIT_SAFE]
ratio = hyg / ief
# Calculate 10-day pct change of the ratio
ratio_change = ratio.pct_change(10).iloc[-1]

if ratio_change < -0.015: # -1.5% drop in ratio
    status = "CRITICAL (Spreads Widening)"
    flags.append("CREDIT_STRESS")
    score_1 = 1
else:
    status = "STABLE"
    score_1 = 0

report_lines.append(f"1. CREDIT PLUMBING: {status} (Ratio Change: {ratio_change:.2%})")

# --- CHECK 2: VOLATILITY STRUCTURE (Fear) ---
# Logic: Simple Defcon Rule for VIX
vix_current = df[VOL_INDEX].iloc[-1]

if vix_current > 20:
    status = "ELEVATED (Defcon Trigger)"
    flags.append("HIGH_VOLATILITY")
    score_2 = 1
else:
    status = "NORMAL"
    score_2 = 0

report_lines.append(f"2. VOLATILITY:      {status} (VIX: {vix_current:.2f})")

# --- CHECK 3: CURRENCY SPIKE (Global Margin Call) ---
# Logic: If Dollar spikes > 2% in 5 days
dxy = df[CURRENCY]
dxy_change = dxy.pct_change(5).iloc[-1]

if dxy_change > 0.02:
    status = "SPIKING (Risk Off)"
    flags.append("CURRENCY_SHOCK")
    score_3 = 1
else:
    status = "STABLE"
    score_3 = 0

report_lines.append(f"3. US DOLLAR:       {status} (5-Day Move: {dxy_change:.2%})")

# --- CHECK 4: INTERNAL BREADTH (Dad's Swarm Data) ---
# Placeholder: In production, this comes from his "Current Recs.csv"
# We define "Caution" if < 50% of stocks have positive forecasts
# For simulation, let's assume it's NORMAL (change manually to test)
dad_breadth_ratio = 0.65 # 65% Positive

if dad_breadth_ratio < 0.50:
    status = "DIVERGENCE (Internal Weakness)"
    flags.append("BAD_BREADTH")
    score_4 = 1
else:
    status = "SUPPORTIVE"
    score_4 = 0

report_lines.append(f"4. SWARM BREADTH:   {status} (Ratio: {dad_breadth_ratio:.0%})")


# ==========================================
# 3. CALCULATE JUDGMENT LEVEL
# ==========================================
# Base Level is 3 (Normal)
# Each Flag adds risk levels
total_flags = len(flags)

if total_flags == 0:
    level = 3
    level_name = "NORMAL OPS"
    action = "Standard Allocations."
elif total_flags == 1:
    level = 4
    level_name = "WATCHLIST"
    action = "No Leverage. Monitor Closely."
elif total_flags == 2:
    level = 5
    level_name = "CAUTION"
    action = "Cap Sector Exposure at 20%. Raise Cash."
elif total_flags >= 3:
    level = 7
    level_name = "EMERGENCY"
    action = "MAX DEFENSE. 100% Cash/Hedged."

# ==========================================
# 4. PRINT THE "PRE-FLIGHT REPORT"
# ==========================================
print("\n" + "="*50)
print(f"   ALPHA SWARM GOVERNANCE REPORT")
print(f"   Date: {datetime.now().strftime('%Y-%m-%d')}")
print("="*50)
print(f"\nJUDGMENT OVERLAY:  LEVEL {level} ({level_name})")
print("-" * 50)
for line in report_lines:
    print(line)
print("-" * 50)
print(f"FLAGS DETECTED:    {flags if flags else 'None'}")
print(f"REQUIRED ACTION:   {action}")
print("="*50)
print("="*50)
print(f"REPORT SAVED TO: {os.getcwd()}\\governance_status.txt")
input("\nPRESS ENTER TO EXIT...")  # <--- ADD THIS LINE

# FORCE SAVE TO THE SAME FOLDER AS THE SCRIPT
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "governance_status.txt")

with open(file_path, "w") as f:
    f.write(f"LEVEL: {level}\nNAME: {level_name}\nFLAGS: {flags}\nACTION: {action}")

print(f"\n[SUCCESS] File saved at: {file_path}")
input("\nPRESS ENTER TO EXIT...")

# Save this for the LLM to read later
with open("governance_status.txt", "w") as f:
    f.write(f"LEVEL: {level}\nNAME: {level_name}\nFLAGS: {flags}\nACTION: {action}")


