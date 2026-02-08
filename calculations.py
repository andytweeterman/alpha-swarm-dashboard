import pandas as pd
import numpy as np
from datetime import timedelta

def calculate_ppo(price):
    ema12 = price.ewm(span=12, adjust=False).mean()
    ema26 = price.ewm(span=26, adjust=False).mean()
    ppo_line = ((ema12 - ema26) / ema26) * 100
    signal_line = ppo_line.ewm(span=9, adjust=False).mean()
    hist = ppo_line - signal_line
    return ppo_line, signal_line, hist

def calculate_cone(price):
    window = 20
    sma = price.rolling(window=window).mean()
    std = price.rolling(window=window).std()
    upper_band = sma + (1.28 * std)
    lower_band = sma - (1.28 * std)
    return sma, std, upper_band, lower_band

def generate_forecast(start_date, last_price, last_std, days=30):
    future_dates = [start_date + timedelta(days=i) for i in range(1, days + 1)]
    drift = 0.0003
    future_mean = [last_price * ((1 + drift) ** i) for i in range(1, days + 1)]
    future_upper = []
    future_lower = []

    for i in range(1, days + 1):
        time_factor = np.sqrt(i)
        width = (1.28 * last_std) + (last_std * 0.1 * time_factor)
        future_upper.append(future_mean[i-1] + width)
        future_lower.append(future_mean[i-1] - width)

    return future_dates, future_mean, future_upper, future_lower

def calculate_governance_history(data):
    closes = data['Close']
    df = pd.DataFrame(index=closes.index)
    df['Credit_Ratio'] = closes["HYG"] / closes["IEF"]
    df['Credit_Delta'] = df['Credit_Ratio'].pct_change(10)
    df['VIX'] = closes["^VIX"]
    df['Breadth_Ratio'] = closes["RSP"] / closes["SPY"]
    df['Breadth_Delta'] = df['Breadth_Ratio'].pct_change(20)
    df['DXY_Delta'] = closes["DX-Y.NYB"].pct_change(5)

    CREDIT_TRIG = -0.015; VIX_PANIC = 24.0; BREADTH_TRIG = -0.025; DXY_SPIKE = 0.02

    df['Level_7'] = (df['Credit_Delta'] < CREDIT_TRIG) | (df['DXY_Delta'] > DXY_SPIKE)
    df['Level_5'] = (df['VIX'] > VIX_PANIC) & (df['Breadth_Delta'] < BREADTH_TRIG)
    df['Level_4'] = (df['Breadth_Delta'] < BREADTH_TRIG) | (df['VIX'] > VIX_PANIC)

    latest = df.iloc[-1]
    if latest['Level_7']: status, color, reason = "EMERGENCY", "red", "Structural/Policy Failure"
    elif latest['Level_5']: status, color, reason = "CAUTION", "orange", "Market Divergence"
    elif latest['Level_4']: status, color, reason = "WATCHLIST", "yellow", "Elevated Risk Monitors"
    else: status, color, reason = "NORMAL OPS", "#00CC00", "System Integrity Nominal"

    return df, status, color, reason
