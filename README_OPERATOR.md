# Operator's Guide (For Business Owner)

This guide explains how to use the dashboard on a weekly basis.

## How to Update the Forecast
1. Save your Excel forecast as `^GSPC.csv`.
2. Drop this file into the root folder of the dashboard.
3. The "Deep Dive" chart will update automatically when this file is detected.

## How to Read the "Safety Level"
- **Green**: Comfort Zone (Safe to proceed)
- **Yellow**: Caution (Be careful)
- **Red**: Defensive Mode (Take protective measures)

## How to Create Content
1. Navigate to the "Swarm Deep Dive" chart.
2. Take a screenshot of the chart.
3. Paste the screenshot into your WordPress blog post.

## Troubleshooting
If the screen goes blank, check that your CSV file (`^GSPC.csv`) has the following columns:
- `FP1`
- `FP3`
- `FP6`

*Note: The file must also contain `Date` and `Tstk_Adj` columns for the system to process it correctly.*
