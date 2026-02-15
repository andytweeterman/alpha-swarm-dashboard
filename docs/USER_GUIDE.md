# MacroEffects | User Guide

## Introduction
**MacroEffects** is a risk-aware market intelligence platform designed to help investors "Outthink the Market." It combines institutional-grade quantitative swarms with human strategic insight to provide a clear, comforting view of market conditions.

## Getting Started
The dashboard is optimized for both desktop (wide view) and mobile devices.
* **Theme:** Toggle between **Dark Mode** (Institutional) and **Light Mode** (Standard) using the menu in the top right.

---

## 1. Global Asset Grid
The top section provides an immediate "Pulse Check" on the major asset classes.
* **Indices:** S&P 500 (SPY), Dow Jones (^DJI), Nasdaq (^IXIC).
* **Risk Monitors:** VIX Index (Market Fear), Gold, and Crude Oil.
* **Sparklines:** Mini-charts showing the last 30 days of price action to highlight immediate trends.

## 2. Swarm Deep Dive (The Chart)
This is the core engine of the platform. It visualizes where the market *is* versus where the swarm models predict it *should be*.

* **Fair Value Cone (Blue):** Represents the "Normal" price range based on historical volatility (±1.28 standard deviations). If price stays inside the cone, the market is behaving normally.
* **Strategist Forecast (Gold Dotted Line):** Represents the proprietary "Alpha Swarm" prediction for the next 1–6 months.
* **View Modes:**
    * **Tactical (60-Day Zoom):** Best for short-term trading. Focuses on the 30-day forecast.
    * **Strategic (2-Year History):** Best for long-term perspective. Highlights major macro trends.

## 3. Safety & Stress Tests (Governance)
Instead of a "Black Box," MacroEffects uses a transparent "Traffic Light" system to monitor systemic risk.

### **The Safety Levels**
* 🟢 **COMFORT ZONE (Green):** System integrity is nominal. Markets are functioning normally. Standard allocations apply.
* 🟡 **CAUTION (Yellow):** Elevated risk detected. Monitors (VIX or Credit) are flashing warnings. Review leverage.
* 🔴 **DEFENSIVE MODE (Red):** Structural stress detected. The swarm recommends moving to cash or hedged positions.

### **The Monitors**
* **Risk (VIX):** Measures market calmness. A spike >24.0 triggers a warning.
* **Credit Spreads:** Monitors the bond market (HYG/IEF). Widening spreads indicate economic stress.
* **Market Breadth:** Compares the "Average Stock" (RSP) to the "Giants" (SPY). Narrowing breadth is an early warning sign of a top.
* **US Dollar (DXY):** significant spikes in the dollar often correlate with risk-off events.

## 4. Tactical Horizons
Actionable momentum signals based on the **PPO (Percentage Price Oscillator)**:
* **1 WEEK (Momentum):** Is the immediate buying pressure rising or falling?
* **1 MONTH (Trend):** Is the medium-term trend Bullish or Bearish?
* **6 MONTH (Structural):** Aligns with the overall Safety Level.

---

## 5. Strategist View
This tab displays the latest market commentary and forecasts from the Chief Strategist. It explains the *Why* behind the numbers.

---

## Operator's Manual (Admin Only)
*Instructions for updating the forecast data.*

**How to Update the Swarm:**
1.  **Generate Data:** Run your weekly models in Excel.
2.  **Save as CSV:** Save the forecast sheet as a CSV file named **`^GSPC.csv`**.
    * *Required Columns:* `Date`, `Tstk_Adj`, `FP1`, `FP3`, `FP6`.
3.  **Upload:** Drag and drop the file into the main `alpha-swarm-dashboard` folder (overwrite the old file).
4.  **Verify:** The "Deep Dive" chart and "Strategist" tab will update automatically.

**Publishing to WordPress:**
* Use the "Snipping Tool" to screenshot the **Deep Dive Chart**.
* Paste the image into your blog post to support your narrative.

---

### Disclaimer
*MacroEffects provides market analysis for informational purposes only. It does not constitute financial advice. Always conduct your own due diligence before making investment decisions.*