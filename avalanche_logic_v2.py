import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

print("--- [ALPHA SWARM: AVALANCHE GOVERNANCE V2] ---")

# ==========================================
# 1. CONFIGURATION & THRESHOLDS
# ==========================================
# Tickers
CREDIT_RISKY = "HYG"    # High Yield Corporate Bond ETF
CREDIT_SAFE = "IEF"     # 7-10 Year Treasury Bond ETF
VOL_INDEX = "^VIX"      # CBOE Volatility Index
CURRENCY = "DX-Y.NYB"   # US Dollar Index

# Thresholds (Tuned based on Dad's "Bad Dates" Analysis)
CREDIT_TRIGGER_PCT = -0.015  # If HYG underperforms IEF by 1.5% in 10 days
VIX_PANIC_LEVEL = 24.0       # Elevated from 20 to reduce false positives
DXY_SPIKE_PCT = 0.02         # 2% Dollar Spike in 5 days

# ==========================================
# 2. FETCH MACRO DATA
# ==========================================
def fetch_data():
    tickers = [CREDIT_RISKY, CREDIT_SAFE, VOL_INDEX, CURRENCY]
    print(f"Fetching live macro data for: {tickers}...")
    try:
        # Download last 2 months to ensure enough runway for moving averages
        data = yf.download(tickers, period="2mo", progress=False)['Close']
        if data.empty:
            raise ValueError("No data returned")
        return data
    except Exception as e:
        print(f"[CRITICAL ERROR] Could not fetch data: {e}")
        print("Check your internet connection.")
        sys.exit()

df = fetch_data()

# ==========================================
# 3. RUN THE "SNOWPACK" CHECKS
# ==========================================
flags = []
report_lines = []

# --- CHECK 1: CREDIT PLUMBING (The Primary Trigger) ---
# Logic: Ratio of HYG (Junk) to IEF (Safe). If this ratio drops, spreads are widening.
hyg = df[CREDIT_RISKY]
ief = df[CREDIT_SAFE]
credit_ratio = hyg / ief
# 10-Day Rate of Change
credit_change = credit_ratio.pct_change(10).iloc[-1]

if credit_change < CREDIT_TRIGGER_PCT:
    credit_status = "CRITICAL (Spreads Widening)"
    is_credit_broken = True
    flags.append("CREDIT_EVENT")
else:
    credit_status = "STABLE"
    is_credit_broken = False

report_lines.append(f"1. CREDIT SPREADS (Primary): {credit_status} | Ratio Delta: {credit_change:.2%}")

# --- CHECK 2: VOLATILITY STRUCTURE ---
vix_current = df[VOL_INDEX].iloc[-1]
# Simple check for now (Level > 24 implies structural fear)
if vix_current > VIX_PANIC_LEVEL:
    vol_status = "ELEVATED"
    is_vol_broken = True
    flags.append("VOLATILITY_SPIKE")
else:
    vol_status = "NORMAL"
    is_vol_broken = False

report_lines.append(f"2. VOLATILITY CHECK:         {vol_status} | VIX: {vix_current:.2f}")

# --- CHECK 3: US DOLLAR STAMPEDE ---
dxy = df[CURRENCY]
dxy_change = dxy.pct_change(5).iloc[-1]

if dxy_change > DXY_SPIKE_PCT:
    dxy_status = "LIQUIDITY CRUNCH (Dollar Spiking)"
    is_dxy_broken = True
    flags.append("DOLLAR_SHOCK")
else:
    dxy_status = "STABLE"
    is_dxy_broken = False

report_lines.append(f"3. DOLLAR LIQUIDITY:         {dxy_status} | 5-Day Move: {dxy_change:.2%}")

# --- CHECK 4: INTERNAL BREADTH (Placeholder for Dad's Data) ---
# We assume neutral for now unless manually set
breadth_status = "NEUTRAL" 
report_lines.append(f"4. INTERNAL SWARM BREADTH:   {breadth_status} (Auto-Pass)")


# ==========================================
# 4. CALCULATE GOVERNANCE LEVEL (HIERARCHY LOGIC)
# ==========================================
# BASELINE: Level 3 (Normal Ops)
level = 3
level_name = "NORMAL OPS"
action = "Standard Allocations."

# LOGIC RULE 1: If Credit Breaks, we go straight to Level 5 (Caution)
if is_credit_broken:
    level = 5
    level_name = "CAUTION (CREDIT EVENT)"
    action = "Defensive Posture. Max 20% Sector Exposure. Cash Raise."
    
    # LOGIC RULE 2: If Credit Breaks AND Vol/Dollar breaks -> EMERGENCY
    if is_vol_broken or is_dxy_broken:
        level = 7
        level_name = "EMERGENCY (SYSTEM FAILURE)"
        action = "MAX DEFENSE. 100% Cash or Hedged. The dam has broken."

# LOGIC RULE 3: If Credit is Fine, but Vol/Dollar acting up -> WATCHLIST
elif is_vol_broken or is_dxy_broken:
    level = 4
    level_name = "WATCHLIST (Choppy)"
    action = "No Leverage. Tighten Stops. Monitor Credit closely."

# ==========================================
# 5. OUTPUT & SAVE
# ==========================================
print("\n" + "="*60)
print(f"   ALPHA SWARM GOVERNANCE REPORT (Weighted Logic)")
print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("="*60)
print(f"\nJUDGMENT OVERLAY:  LEVEL {level} ({level_name})")
print("-" * 60)
for line in report_lines:
    print(line)
print("-" * 60)
print(f"PRIMARY TRIGGER:   {'FAIL' if is_credit_broken else 'PASS'}")
print(f"FLAGS DETECTED:    {flags if flags else 'None'}")
print(f"REQUIRED ACTION:   {action}")
print("="*60)

# Save for Narrative Engine
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "governance_status.txt")

with open(file_path, "w") as f:
    f.write(f"LEVEL: {level}\nNAME: {level_name}\nFLAGS: {flags}\nACTION: {action}")

print(f"\n[SUCCESS] Governance Status saved to: {file_path}")
input("\nPress ENTER to exit...")