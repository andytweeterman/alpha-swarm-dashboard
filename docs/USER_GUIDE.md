# Alpha Swarm User Guide

## Introduction
Alpha Swarm is a comprehensive market intelligence dashboard designed for institutional investors and financial analysts. It provides real-time data, technical analysis, and governance status for global markets.

## Getting Started
To access Alpha Swarm, simply navigate to the application URL. The dashboard is optimized for both desktop and mobile viewing.

### Dark Mode
Toggle between **Institutional Dark Mode** and **Standard Light Mode** using the switch in the sidebar. Dark Mode is recommended for low-light environments and extended viewing sessions.

## Dashboard Overview

### 1. Market Grid
The top section displays key market indices and assets with real-time price updates, percentage changes, and sparklines for quick trend visualization.
- **Indices**: S&P 500 (SPY), Dow Jones (^DJI), Nasdaq (^IXIC)
- **Volatility**: VIX Index (^VIX)
- **Commodities**: Gold (GC=F), Crude Oil (CL=F)

### 2. Swarm Deep Dive
This interactive chart provides a detailed view of market trends and forecasts.
- **Fair Value Cone**: Represents the expected price range based on historical volatility (±1.28 standard deviations).
- **Forecast**: A 30-day projection of potential price movement, visualized with a confidence interval.
- **View Modes**:
    - **Tactical (60-Day Zoom)**: Focuses on short-term price action and immediate trends.
    - **Strategic (2-Year History)**: Provides a longer-term perspective, highlighting major market events.

### 3. Governance Status
The Governance Status indicator monitors systemic risk based on four key metrics:
- **Credit Ratio (HYG/IEF)**: Measures credit market stress.
- **VIX**: Tracks market volatility.
- **Market Breadth (RSP/SPY)**: Assesses the health of the broader market vs. large caps.
- **DXY**: Monitors the strength of the US Dollar.

**Status Levels:**
- **NORMAL OPS (Green)**: System integrity is nominal.
- **WATCHLIST (Yellow)**: Elevated risk monitors triggered.
- **CAUTION (Orange)**: Significant market divergence detected.
- **EMERGENCY (Red)**: Structural or policy failure imminent.

### 4. Tactical Horizons
Provides actionable insights across different timeframes:
- **1 WEEK (Momentum)**: Based on the PPO Histogram. Indicates if momentum is rising or weakening.
- **1 MONTH (Trend)**: Based on the PPO Line. Indicates if the trend is bullish or bearish.
- **6 MONTH (Structural)**: Aligns with the overall Governance Status.

### 5. Strategist View
Displays the latest market commentary and forecasts from the Chief Strategist. This section pulls data directly from a connected Google Sheet or a local backup file, ensuring up-to-date analysis.

## Data Sources
Market data is sourced from `yfinance`, providing reliable and timely information for all tracked assets.

## Disclaimer
This tool provides market analysis for informational purposes only. It does not constitute financial advice. Always conduct your own due diligence before making investment decisions.
