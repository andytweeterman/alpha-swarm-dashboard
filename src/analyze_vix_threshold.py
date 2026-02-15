import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def analyze_vix():
    print("Starting VIX Threshold Analysis...")

    # 1. Fetch data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*10 + 100) # Extra buffer

    print(f"Fetching data from {start_date.date()} to {end_date.date()}...")

    tickers = ["^VIX", "^GSPC"]
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    # Handle MultiIndex columns
    # yfinance returns MultiIndex columns: (Price, Ticker)
    # We want 'Close' price for both
    if isinstance(data.columns, pd.MultiIndex):
        closes = data['Close']
    else:
        # Fallback if structure is different
        closes = data

    # Check if we have the columns
    if "^VIX" not in closes.columns or "^GSPC" not in closes.columns:
        print("Error: Could not find ^VIX or ^GSPC in downloaded data.")
        print(f"Columns found: {closes.columns}")
        return

    vix = closes["^VIX"]
    sp500 = closes["^GSPC"]

    # 2. Identify crossings
    # VIX > 24 AND Prev(VIX) <= 24

    # Create a DataFrame for analysis
    df = pd.DataFrame({
        'VIX': vix,
        'SP500': sp500
    }).dropna()

    df['VIX_Prev'] = df['VIX'].shift(1)
    df['Cross_Above_24'] = (df['VIX'] > 24) & (df['VIX_Prev'] <= 24)

    crossing_dates = df[df['Cross_Above_24']].index

    print(f"Found {len(crossing_dates)} events where VIX crossed above 24.")

    results = []

    for date in crossing_dates:
        # Get S&P 500 price on that date
        try:
            price_t0 = df.loc[date, 'SP500']

            # Find price 3 months later (approx 90 calendar days)
            target_date = date + timedelta(days=90)

            # Find nearest trading day at or after target_date
            # Using searchsorted for efficient binary search on the index
            idx_pos = df.index.searchsorted(target_date)

            if idx_pos >= len(df):
                print(f"Skipping {date.date()}: Not enough future data (less than 3 months left).")
                continue

            date_t3m = df.index[idx_pos]
            price_t3m = df.iloc[idx_pos]['SP500']

            # Calculate return
            pct_return = (price_t3m - price_t0) / price_t0

            # Calculate Max Drawdown in the 3 month period
            # Period from date (exclusive) to date_t3m (inclusive)
            # Find the start index (first date > date)
            start_idx = df.index.searchsorted(date, side='right')
            # End index is idx_pos (inclusive), so slice up to idx_pos + 1
            period_data = df.iloc[start_idx : idx_pos + 1]

            if period_data.empty:
                max_drawdown = 0.0
            else:
                # Measure min price in period vs t0 price.
                min_price = period_data['SP500'].min()
                max_drawdown = (min_price - price_t0) / price_t0

            # Determine outcome description
            outcome_parts = []

            if pct_return > 0:
                outcome_parts.append("Buy Signal")
            else:
                outcome_parts.append("Negative Return")

            if max_drawdown < -0.10:
                outcome_parts.append(f"Major Drawdown ({max_drawdown:.1%})")
            elif max_drawdown < -0.05:
                outcome_parts.append(f"Volatile ({max_drawdown:.1%})")

            outcome = " / ".join(outcome_parts)

            # Classification
            classification = "Buy" if pct_return > 0 else "Crash/Loss"
            if max_drawdown < -0.15:
                classification = "Crash"

            results.append({
                'Date': date,
                'VIX_at_Cross': df.loc[date, 'VIX'],
                'SP500_Price': price_t0,
                'SP500_3M_Price': price_t3m,
                'Return_3M': pct_return,
                'Max_Drawdown_3M': max_drawdown,
                'Outcome': outcome,
                'Classification': classification
            })

        except Exception as e:
            print(f"Error processing {date}: {e}")

    # 3. Generate Report

    md_content = "# VIX Threshold Analysis: Crossing 24\n\n"
    md_content += "## Overview\n"
    md_content += "This research note analyzes historical market data (last 10 years) to evaluate the significance of the VIX crossing above 24. "
    md_content += "Specifically, we examine the S&P 500 performance over the subsequent 3 months to determine if this threshold acts as a 'crash' signal or a 'buy' signal.\n\n"

    md_content += "### Methodology\n"
    md_content += "- **Trigger:** VIX crossing above 24 (daily close > 24, previous close <= 24).\n"
    md_content += "- **Index:** S&P 500 (^GSPC).\n"
    md_content += "- **Horizon:** 3 Months (approx 90 calendar days).\n\n"

    md_content += "### Event Log\n\n"
    md_content += "| Date | VIX Level | S&P 500 3M Return | Max Drawdown (3M) | Outcome |\n"
    md_content += "|---|---|---|---|---|\n"

    for res in results:
        date_str = res['Date'].strftime('%Y-%m-%d')
        vix_val = f"{res['VIX_at_Cross']:.2f}"
        ret_val = f"{res['Return_3M']:.2%}"
        dd_val = f"{res['Max_Drawdown_3M']:.2%}"

        # Color coding for return
        trend_icon = "🟢" if res['Return_3M'] > 0 else "🔴"

        md_content += f"| {date_str} | {vix_val} | {trend_icon} {ret_val} | {dd_val} | {res['Outcome']} |\n"

    md_content += "\n\n### Analysis Summary\n"

    if results:
        avg_return = np.mean([r['Return_3M'] for r in results])
        median_return = np.median([r['Return_3M'] for r in results])
        positive_cases = len([r for r in results if r['Return_3M'] > 0])
        total_cases = len(results)
        win_rate = positive_cases / total_cases

        md_content += f"- **Total Signals:** {total_cases}\n"
        md_content += f"- **Average 3M Return:** {avg_return:.2%}\n"
        md_content += f"- **Median 3M Return:** {median_return:.2%}\n"
        md_content += f"- **Win Rate (Positive Return):** {win_rate:.0%}\n\n"

        md_content += "**Conclusion:**\n"
        if avg_return > 0.02:
             md_content += "Historically, a VIX crossing above 24 has often been a **buy signal** over a 3-month horizon, though it typically involves significant short-term volatility."
        elif avg_return < -0.02:
             md_content += "Historically, a VIX crossing above 24 has often preceded further market declines."
        else:
             md_content += "The signal is mixed, with significant volatility following the event."
    else:
        md_content += "No events found in the specified period."

    output_path = "docs/VIX_Threshold_Analysis.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(md_content)

    print(f"Analysis saved to {output_path}")

if __name__ == "__main__":
    analyze_vix()
