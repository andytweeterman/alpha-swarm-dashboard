import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_market_data():
    """Fetches data from Yahoo Finance with error handling."""
    try:
        # Core tickers for the Swarm
        tickers = ["SPY", "^DJI", "^IXIC", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB", "GC=F", "CL=F"]
        
        # 5 years of data for long-term calculations
        start = (datetime.now() - timedelta(days=1825)).strftime('%Y-%m-%d')
        
        # Download data
        data = yf.download(tickers, start=start, progress=False)
        
        # Basic check to ensure we got data
        if data is None or data.empty:
            return None
            
        return data
    except Exception as e:
        return None

def calc_governance(data):
    """
    Calculates the 'Traffic Light' safety status.
    v56.4 Patch: Added .ffill() and .fillna(False) to handle weekend NaN gaps.
    """
    try:
        # 1. CLEAN THE DATA (The Fix)
        # Forward fill missing weekend data so we don't get NaNs
        closes = data['Close'].ffill()
        
        df = pd.DataFrame(index=closes.index)
        
        # 2. CALCULATE METRICS
        # We wrap this in a try block in case specific tickers are missing
        df['Credit_Ratio'] = closes["HYG"] / closes["IEF"]
        df['Credit_Delta'] = df['Credit_Ratio'].pct_change(10)
        
        # Handle VIX explicitly (it often has gaps)
        if "^VIX" in closes.columns:
            df['VIX'] = closes["^VIX"]
        else:
            df['VIX'] = 0.0 # Default safe if missing
        
        df['Breadth_Ratio'] = closes["RSP"] / closes["SPY"]
        df['Breadth_Delta'] = df['Breadth_Ratio'].pct_change(20)
        
        df['DXY_Delta'] = closes["DX-Y.NYB"].pct_change(5)
        
        # 3. DEFINE TRIGGERS
        CREDIT_TRIG = -0.015
        VIX_PANIC = 24.0
        BREADTH_TRIG = -0.025
        DXY_SPIKE = 0.02
        
        # 4. SAFE LOGIC CHECKS
        # We use fillna(False) to ensure NaNs don't trigger false alarms
        level_7_mask = ((df['Credit_Delta'] < CREDIT_TRIG) | (df['DXY_Delta'] > DXY_SPIKE)).fillna(False)
        level_5_mask = ((df['VIX'] > VIX_PANIC) & (df['Breadth_Delta'] < BREADTH_TRIG)).fillna(False)
        level_4_mask = ((df['Breadth_Delta'] < BREADTH_TRIG) | (df['VIX'] > VIX_PANIC)).fillna(False)
        
        # Store for historical plotting/debugging if needed
        df['Level_7'] = level_7_mask
        df['Level_5'] = level_5_mask
        df['Level_4'] = level_4_mask
        
        # Get latest values safely
        if not df.empty:
            latest = df.iloc[-1]
        else:
            return df, "SYSTEM BOOT", "#888888", "Initializing..."

        # 5. DETERMINE STATUS (Hierarchy: Red -> Orange -> Yellow -> Green)
        if latest['Level_7']: 
            return df, "DEFENSIVE MODE", "#f93e3e", "Structural/Policy Failure"
        elif latest['Level_5']: 
            return df, "CAUTION", "#ffaa00", "Market Divergence"
        elif latest['Level_4']: 
            return df, "WATCHLIST", "#f1c40f", "Elevated Risk Monitors"
        else: 
            return df, "COMFORT ZONE", "#00d26a", "System Integrity Nominal"
            
    except Exception as e:
        # Fallback if math fails completely (e.g. malformed data)
        # We return a neutral/safe dataframe structure to avoid crashing the app
        safe_df = pd.DataFrame()
        return safe_df, "DATA ERROR", "#888888", "Feed Disconnected"

def calc_ppo(price):
    """Calculates Percentage Price Oscillator (Momentum)"""
    # Fix for Series input
    if isinstance(price, pd.DataFrame):
        price = price.iloc[:, 0]
        
    ema12 = price.ewm(span=12, adjust=False).mean()
    ema26 = price.ewm(span=26, adjust=False).mean()
    ppo_line = ((ema12 - ema26) / ema26) * 100
    signal_line = ppo_line.ewm(span=9, adjust=False).mean()
    hist = ppo_line - signal_line
    return ppo_line, signal_line, hist

def calc_cone(price):
    """Calculates the Fair Value Volatility Cone"""
    # Fix for Series input
    if isinstance(price, pd.DataFrame):
        price = price.iloc[:, 0]

    window = 20
    sma = price.rolling(window=window).mean()
    std = price.rolling(window=window).std()
    upper_band = sma + (1.28 * std)
    lower_band = sma - (1.28 * std)
    return sma, std, upper_band, lower_band

def generate_forecast(start_date, last_price, last_std, days=30):
    """Generates the synthetic forecast cone if no strategist data exists"""
    future_dates = [start_date + timedelta(days=i) for i in range(1, days + 1)]
    drift = 0.0003
    i_values = np.arange(1, days + 1)

    future_mean = last_price * ((1 + drift) ** i_values)
    time_factor = np.sqrt(i_values)
    width = (1.28 * last_std) + (last_std * 0.1 * time_factor)

    future_upper = future_mean + width
    future_lower = future_mean - width

    return future_dates, future_mean.tolist(), future_upper.tolist(), future_lower.tolist()

@st.cache_data(ttl=3600)
def load_strategist_data():
    """Ingests the Strategist's Forecast CSV (^GSPC.csv)"""
    try:
        # Priority 1: Check for ^GSPC.csv in root (User Workflow)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        root_file = os.path.join(root_dir, "^GSPC.csv")
        
        if os.path.exists(root_file):
            df = pd.read_csv(root_file)
        else:
            # Priority 2: Look for the file in the data directory
            filename = os.path.join("data", "strategist_forecast.csv")
            if not os.path.exists(filename):
                return None
            df = pd.read_csv(filename)
        
        # Ensure we have the right columns
        required_cols = ['Date', 'Tstk_Adj', 'FP1', 'FP3', 'FP6']
        # flexible check (case insensitive or partial match could be added here, but strict is safer)
        if not all(col in df.columns for col in required_cols):
            return None
            
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        return None

def get_strategist_update():
    """Fetches the Strategist's Commentary (update.csv or Cloud)"""
    try:
        # Priority 1: Environment Variable (Cloud)
        sheet_url = os.environ.get("STRATEGIST_SHEET_URL")

        # Priority 2: Streamlit Secrets
        if not sheet_url:
            try:
                if "STRATEGIST_SHEET_URL" in st.secrets:
                    sheet_url = st.secrets["STRATEGIST_SHEET_URL"]
            except Exception:
                pass

        # If we have a URL
        if sheet_url and "INSERT_YOUR" not in sheet_url:
            return pd.read_csv(sheet_url)

        # Priority 3: Local Fallback
        # We assume a simple CSV with Key/Value pairs exists in data/
        local_path = os.path.join("data", "update.csv")
        if os.path.exists(local_path):
             return pd.read_csv(local_path)
             
        return None
    except Exception:
        return None