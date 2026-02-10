# VIX Threshold Analysis: Crossing 24

## Overview
This research note analyzes historical market data (last 10 years) to evaluate the significance of the VIX crossing above 24. Specifically, we examine the S&P 500 performance over the subsequent 3 months to determine if this threshold acts as a 'crash' signal or a 'buy' signal.

### Methodology
- **Trigger:** VIX crossing above 24 (daily close > 24, previous close <= 24).
- **Index:** S&P 500 (^GSPC).
- **Horizon:** 3 Months (approx 90 calendar days).

### Event Log

| Date | VIX Level | S&P 500 3M Return | Max Drawdown (3M) | Outcome |
|---|---|---|---|---|
| 2015-12-11 | 24.39 | 🔴 -1.13% | -9.11% | Negative Return / Volatile (-9.1%) |
| 2016-01-07 | 24.99 | 🟢 6.36% | -5.87% | Buy Signal / Volatile (-5.9%) |
| 2016-01-13 | 25.22 | 🟢 9.07% | -3.24% | Buy Signal |
| 2016-01-15 | 27.02 | 🟢 10.77% | -2.73% | Buy Signal |
| 2016-01-25 | 24.15 | 🟢 11.23% | -2.56% | Buy Signal |
| 2016-02-08 | 26.00 | 🟢 11.07% | -1.31% | Buy Signal |
| 2016-06-24 | 25.76 | 🟢 6.86% | -1.81% | Buy Signal |
| 2018-02-05 | 37.32 | 🟢 0.89% | -2.56% | Buy Signal |
| 2018-03-23 | 24.87 | 🟢 6.24% | -0.25% | Buy Signal |
| 2018-10-11 | 24.98 | 🔴 -5.26% | -13.83% | Negative Return / Major Drawdown (-13.8%) |
| 2018-10-24 | 25.23 | 🔴 -0.87% | -11.48% | Negative Return / Major Drawdown (-11.5%) |
| 2018-12-17 | 24.52 | 🟢 11.27% | -7.65% | Buy Signal / Volatile (-7.7%) |
| 2019-01-03 | 25.45 | 🟢 17.38% | 3.43% | Buy Signal |
| 2019-08-05 | 24.59 | 🟢 8.21% | -0.15% | Buy Signal |
| 2020-02-24 | 25.03 | 🔴 -7.26% | -30.64% | Negative Return / Major Drawdown (-30.6%) |
| 2020-08-11 | 24.03 | 🟢 6.50% | -2.90% | Buy Signal |
| 2020-08-27 | 24.47 | 🟢 4.16% | -7.11% | Buy Signal / Volatile (-7.1%) |
| 2020-08-31 | 26.41 | 🟢 3.47% | -7.52% | Buy Signal / Volatile (-7.5%) |
| 2020-11-12 | 25.35 | 🟢 10.54% | 0.58% | Buy Signal |
| 2020-12-14 | 24.72 | 🟢 8.81% | 1.09% | Buy Signal |
| 2020-12-21 | 25.16 | 🟢 6.65% | -0.21% | Buy Signal |
| 2021-01-04 | 26.97 | 🟢 10.19% | 0.37% | Buy Signal |
| 2021-01-11 | 24.08 | 🟢 8.64% | -2.25% | Buy Signal |
| 2021-01-15 | 24.34 | 🟢 10.67% | -1.43% | Buy Signal |
| 2021-01-27 | 37.21 | 🟢 11.62% | -0.97% | Buy Signal |
| 2021-02-25 | 28.89 | 🟢 9.57% | -1.59% | Buy Signal |
| 2021-03-02 | 24.10 | 🟢 8.57% | -2.63% | Buy Signal |
| 2021-05-12 | 27.59 | 🟢 9.20% | 1.22% | Buy Signal |
| 2021-09-20 | 25.71 | 🟢 4.83% | -1.31% | Buy Signal |
| 2021-11-26 | 28.62 | 🔴 -6.66% | -8.03% | Negative Return / Volatile (-8.0%) |
| 2021-11-30 | 27.19 | 🔴 -4.23% | -7.48% | Negative Return / Volatile (-7.5%) |
| 2022-01-20 | 25.59 | 🔴 -0.52% | -6.96% | Negative Return / Volatile (-7.0%) |
| 2022-02-03 | 24.35 | 🔴 -3.96% | -7.72% | Negative Return / Volatile (-7.7%) |
| 2022-02-11 | 27.36 | 🔴 -11.06% | -11.06% | Negative Return / Major Drawdown (-11.1%) |
| 2022-04-11 | 24.37 | 🔴 -12.65% | -16.90% | Negative Return / Major Drawdown (-16.9%) |
| 2022-04-22 | 28.21 | 🔴 -6.39% | -14.16% | Negative Return / Major Drawdown (-14.2%) |
| 2022-06-09 | 26.09 | 🔴 -0.94% | -8.74% | Negative Return / Volatile (-8.7%) |
| 2022-07-26 | 24.69 | 🔴 -3.16% | -8.77% | Negative Return / Volatile (-8.8%) |
| 2022-08-23 | 24.11 | 🔴 -4.33% | -13.36% | Negative Return / Major Drawdown (-13.4%) |
| 2022-08-26 | 25.56 | 🔴 -0.78% | -11.85% | Negative Return / Major Drawdown (-11.8%) |
| 2022-09-13 | 27.27 | 🟢 1.47% | -9.04% | Buy Signal / Volatile (-9.0%) |
| 2022-11-15 | 24.54 | 🟢 3.65% | -5.22% | Buy Signal / Volatile (-5.2%) |
| 2022-12-12 | 25.00 | 🔴 -3.38% | -5.20% | Negative Return / Volatile (-5.2%) |
| 2023-03-10 | 24.80 | 🟢 11.20% | -0.15% | Buy Signal |
| 2023-03-15 | 26.14 | 🟢 12.26% | 0.63% | Buy Signal |
| 2023-03-17 | 25.51 | 🟢 13.00% | 0.52% | Buy Signal |
| 2024-08-05 | 38.57 | 🟢 10.15% | 0.25% | Buy Signal |
| 2024-12-18 | 27.62 | 🔴 -4.39% | -5.97% | Negative Return / Volatile (-6.0%) |
| 2025-03-06 | 24.87 | 🟢 4.05% | -13.17% | Buy Signal / Major Drawdown (-13.2%) |
| 2025-03-10 | 27.86 | 🟢 6.97% | -11.25% | Buy Signal / Major Drawdown (-11.3%) |
| 2025-04-03 | 30.02 | 🟢 15.40% | -7.67% | Buy Signal / Volatile (-7.7%) |
| 2025-05-06 | 24.76 | 🟢 12.90% | 0.43% | Buy Signal |
| 2025-10-16 | 25.31 | 🟢 4.49% | -1.36% | Buy Signal |


### Analysis Summary
- **Total Signals:** 53
- **Average 3M Return:** 4.37%
- **Median 3M Return:** 6.36%
- **Win Rate (Positive Return):** 68%

**Conclusion:**
Historically, a VIX crossing above 24 has often been a **buy signal** over a 3-month horizon, though it typically involves significant short-term volatility.