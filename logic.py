import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

@st.cache_data(ttl=3600)
def fetch_market_data():
    try:
        tickers = ["SPY", "^DJI", "^IXIC", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB", "GC=F", "CL=F"]
        start = (datetime.now() - timedelta(days=1825)).strftime('%Y-%m-%d')
        data = yf.download(tickers, start=start, progress=False)
        return data
    except Exception:
        return None

def calc_governance(data):
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
    if latest['Level_7']: return df, "EMERGENCY", "#f93e3e", "Structural/Policy Failure"
    elif latest['Level_5']: return df, "CAUTION", "#ffaa00", "Market Divergence"
    elif latest['Level_4']: return df, "WATCHLIST", "#f1c40f", "Elevated Risk Monitors"
    else: return df, "NORMAL OPS", "#00d26a", "System Integrity Nominal"

@st.cache_data(ttl=3600)
def load_strategist_data():
    """Ingests the Strategist's Forecast CSV (data/strategist_forecast.csv)"""
    try:
        # Look for the file in the data directory
        filename = os.path.join("data", "strategist_forecast.csv")

        if not os.path.exists(filename):
            return None

        df = pd.read_csv(filename)

        # Ensure we have the right columns
        required_cols = ['Date', 'Tstk_Adj', 'FP1', 'FP3', 'FP6']
        if not all(col in df.columns for col in required_cols):
            return None

        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        return None

def get_strategist_update():
    """Fetches the Strategist's Update from Env Var or Local File"""
    try:
        # Priority 1: Environment Variable
        sheet_url = os.environ.get("STRATEGIST_SHEET_URL")

        # Priority 2: Streamlit Secrets (if available)
        if not sheet_url:
            try:
                if "STRATEGIST_SHEET_URL" in st.secrets:
                    sheet_url = st.secrets["STRATEGIST_SHEET_URL"]
            except Exception:
                pass

        # If we have a URL and it's not a placeholder
        if sheet_url and "INSERT_YOUR" not in sheet_url:
            return pd.read_csv(sheet_url)

        # Priority 3: Local Fallback
        return pd.read_csv("data/update.csv")
    except Exception:
        return None

def calc_ppo(price):
    ema12 = price.ewm(span=12, adjust=False).mean()
    ema26 = price.ewm(span=26, adjust=False).mean()
    ppo_line = ((ema12 - ema26) / ema26) * 100
    signal_line = ppo_line.ewm(span=9, adjust=False).mean()
    hist = ppo_line - signal_line
    return ppo_line, signal_line, hist

def calc_cone(price):
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
