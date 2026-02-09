import os
import datetime

# ==========================================
# 1. READ THE GOVERNANCE REPORT
# ==========================================
# We find the file you just created
script_dir = os.path.dirname(os.path.abspath(__file__))
gov_file = os.path.join(script_dir, "governance_status.txt")

try:
    with open(gov_file, "r") as f:
        gov_data = f.read()
    print("[SUCCESS] Governance Report Loaded.")
except FileNotFoundError:
    print("[ERROR] Could not find governance_status.txt. Run avalanche_logic.py first!")
    exit()

# ==========================================
# 2. INPUT THE SWARM SIGNAL (Manual for now)
# ==========================================
# In the future, this comes automatically from your Dad's Excel file.
# For today, we hard-code a "Test Case" to see if the LLM can write it.
SWARM_SECTOR = "Technology (XLK)"
SWARM_SIGNAL = "Bullish Accumulation"
SWARM_SCORE = "8.5 / 10"
KEY_TICKERS = "NVDA, AMD, MSFT"
CONTEXT = "Price broke above 50-day moving average. Volume increasing."

# ==========================================
# 3. BUILD THE "MASTER PROMPT"
# ==========================================
# This is the "Persona Engineering" we discussed.

prompt = f"""
*** SYSTEM INSTRUCTION ***
You are the Chief Investment Strategist for 'The Alpha Swarm,' a quantitative research firm. 
Your tone is Institutional, Data-Driven, and concise. You do not hype. You analyze probability.

*** INPUT DATA ***
1. DATE: {datetime.datetime.now().strftime("%Y-%m-%d")}
2. GOVERNANCE STATUS:
{gov_data}

3. SWARM SIGNAL:
- Target Sector: {SWARM_SECTOR}
- Direction: {SWARM_SIGNAL}
- Quant Score: {SWARM_SCORE}
- Key Tickers: {KEY_TICKERS}
- Technical Context: {CONTEXT}

*** YOUR TASK ***
Write a 3-paragraph "Morning Brief" for our institutional clients.

PARAGRAPH 1: THE SIGNAL
Summarize the Swarm's view on {SWARM_SECTOR}. Use the Quant Score and Technical Context to explain *why* the algorithm likes it.

PARAGRAPH 2: THE GOVERNANCE CHECK
Reference the "Judgment Overlay" status found in the Input Data. 
- Since we are at Level 3 (Normal Ops), explain that the macro environment (Credit, VIX, Dollar) is currently supporting risk assets. 
- Mention specifically that "Credit Plumbing" and "Volatility" are stable.

PARAGRAPH 3: THE TRADE
Conclude with a clear directive. "The Swarm favors overweighting {SWARM_SECTOR}..."

*** OUTPUT FORMAT ***
Do not include chatty intros. Start directly with the headline.
"""

# ==========================================
# 4. SAVE & PRINT
# ==========================================
output_file = os.path.join(script_dir, "FINAL_LLM_PROMPT.txt")

with open(output_file, "w") as f:
    f.write(prompt)

print("\n" + "="*50)
print("   NARRATIVE ENGINE: PROMPT GENERATED")
print("="*50)
print(f"1. Open the file: {output_file}")
print("2. Copy all text.")
print("3. Paste into your Local LLM.")
print("="*50)
input("\nPRESS ENTER TO EXIT...")