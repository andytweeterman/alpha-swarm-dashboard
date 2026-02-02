import os
import datetime

# ==========================================
# 1. READ THE GOVERNANCE REPORT (From Task 3)
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
gov_file = os.path.join(script_dir, "governance_status.txt")

try:
    with open(gov_file, "r") as f:
        gov_data = f.read()
    print("[SUCCESS] Governance Report Loaded.")
except FileNotFoundError:
    print("[WARN] governance_status.txt not found. Using default Level 3.")
    gov_data = "LEVEL: 3\nNAME: NORMAL OPS\nFLAGS: []\nACTION: Standard Allocations."

# ==========================================
# 2. INPUT THE REAL "SWARM" DATA
# ==========================================
# These values come directly from your analysis of ^GSPC.csv
# ---------------------------------------------------------
ASSET = "S&P 500 (SPX)"
CURRENT_PRICE = 6978.03
FORECAST_1WK = -0.0036  # -0.36% (From your file)
FORECAST_DIRECTION = "Negative Mean Reversion"
MODEL_SIGMA = 0.0302    # 3.02% (The Standard Deviation we calculated)
TERM_STRUCTURE = "Inverted (Negative short-term, Positive long-term)"

# ==========================================
# 3. BUILD THE "SCIENTIFIC" PROMPT
# ==========================================
prompt = f"""
*** SYSTEM INSTRUCTION ***
You are the Senior Quantitative Risk Manager for 'Alpha Swarm.'
Your job is to interpret probabilistic model outputs for institutional clients.

*** TONE GUIDELINES ***
1.  **SCIENTIFIC:** Speak in terms of probabilities, distributions, and skew.
2.  **NO JARGON:** Do NOT use Technical Analysis terms (e.g., "Breakout," "Support/Resistance," "Moving Average," "Bullish/Bearish").
3.  **EVIDENCE-BASED:** Ground every claim in the provided data. If the forecast is small, acknowledge the uncertainty.
4.  **CONCISE:** No fluff. No "The market is interesting today." Get to the numbers.

*** INPUT DATA (REAL TIME) ***
1. DATE: {datetime.datetime.now().strftime("%Y-%m-%d")}
2. ASSET: {ASSET} at {CURRENT_PRICE}
3. MODEL OUTPUTS:
   - 1-Week Forecast Mean: {FORECAST_1WK:.2%} (Negative Skew)
   - Model Volatility (Sigma): {MODEL_SIGMA:.2%}
   - Term Structure: {TERM_STRUCTURE}
4. GOVERNANCE STATUS (RISK OVERLAY):
{gov_data}

*** YOUR TASK ***
Write a 3-paragraph "Risk & Allocation Brief."

PARAGRAPH 1: THE PROBABILISTIC FORECAST
State the model's projected path. 
- Instead of saying "We are bearish," say "The model detects a negative skew of {FORECAST_1WK:.2%}."
- Mention that this falls within one standard deviation ({MODEL_SIGMA:.2%}) of normal variance.
- Explain the "Term Structure" (Short term pain, Long term gain).

PARAGRAPH 2: THE SYSTEMIC RISK CHECK
Reference the "Governance Status."
- If Level 3 (Normal Ops), explain that while the *Forecast* is negative, the *Systemic Backdrop* (Liquidity/Credit) remains stable.
- This creates a specific nuance: "Price Risk is elevated, but Structural Risk is low."

PARAGRAPH 3: POSITIONING
Conclude with the allocation decision.
- "Given the negative expected value over the 1-week horizon, the Swarm suggests reducing active leverage while maintaining core equity exposure."

*** OUTPUT ***
(Produce the Brief below. Do not add introductory text.)
"""

# ==========================================
# 4. SAVE & PRINT
# ==========================================
output_file = os.path.join(script_dir, "FINAL_QUANT_PROMPT.txt")

with open(output_file, "w") as f:
    f.write(prompt)

print("\n" + "="*50)
print("   NARRATIVE ENGINE V2: QUANT MODE ACTIVE")
print("="*50)
print(f"PROMPT SAVED TO: {output_file}")
print("1. Open the file.")
print("2. Paste into your LLM.")
print("3. Verify the tone is 'Scientific' not 'Salesy'.")
input("\nPRESS ENTER TO EXIT...")