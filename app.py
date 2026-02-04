import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE SETUP (TRUE BLACK MODE)
# ==========================================
st.set_page_config(page_title="Alpha Swarm", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, div, span, li { color: #E0E0E0 !important; }
    div[data-testid="stMetricValue"] { color: #00FF00 !important; }
    .big-badge {
        font-size: 24px; font-weight: bold; padding: 15px;
        border-radius: 5px; text-align: center; margin-bottom: 20px;
        border: 1px solid #333;
    }
    div[data-testid="stExpander"] { background-color: #0E1117; border: 1px solid #333; border-radius: 5px; }
    div[data-testid="stExpander"] details { background-color: #0E1117; }
    div[data-testid="stExpander"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. THE ENGINE
# ==========================================
@st.cache_data(ttl=3600)
def fetch_data():
    with st.spinner('Downloading Market Data from Yahoo Finance...'):
        tickers = ["SPY", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB"]
        start = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        data = yf.download(tickers, start=start, progress=False)
    return data

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
    
    # Swarm Mean Projection (Placeholder Logic)
    drift = 0.0003
    future_mean = [last_price * ((1 + drift) ** i) for i in range(1, days + 1)]
    
    # Uncertainty Cone (Sqrt Time)
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

# ==========================================
# 3. THE UI RENDER
# ==========================================
st.title("🛡️ ALPHA SWARM GOVERNANCE")
st.markdown("### Live Structural Risk & PPO Momentum Monitor")
st.divider()

try:
    full_data = fetch_data()
    gov_df, status, color, reason = calculate_governance_history(full_data)
    
    spy_close = full_data['Close']['SPY']
    ppo, sig, hist = calculate_ppo(spy_close)
    sma, std, upper_cone, lower_cone = calculate_cone(spy_close)
    
    # GENERATE FORECAST
    last_date = spy_close.index[-1]
    last_val = spy_close.iloc[-1]
    last_dev = std.iloc[-1]
    f_dates, f_mean, f_upper, f_lower = generate_forecast(last_date, last_val, last_dev, days=30)
    
    # ------------------
    # TOP SECTION: BADGES
    # ------------------
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div class="big-badge" style="background-color: {color}; color: white;">GOVERNANCE STATUS: {status}</div>', unsafe_allow_html=True)
        st.caption(f"Reason: {reason}")
    with col2:
        latest_vix = full_data['Close']['^VIX'].iloc[-1]
        st.metric("VIX Level", f"{latest_vix:.2f}", delta_color="inverse")

    # ------------------
    # HORIZON STRIP
    # ------------------
    st.subheader("⏱️ Tactical Horizons")
    h1, h2, h3 = st.columns(3)
    with h1:
        st.info("**1 WEEK (Momentum)**")
        st.markdown("🟢 **RISING**" if hist.iloc[-1] > 0 else "🔴 **WEAKENING**")
        st.caption("PPO Histogram")
    with h2:
        st.info("**1 MONTH (Trend)**")
        st.markdown("🟢 **BULLISH**" if ppo.iloc[-1] > 0 else "🔴 **BEARISH**")
        st.caption(f"PPO Line ({ppo.iloc[-1]:.2f})")
    with h3:
        st.info("**6 MONTH (Structural)**")
        st.markdown("🟢 **SAFE**" if status == "NORMAL OPS" else f"🔴 **{status}**")
        st.caption("Swarm Governance")

    st.divider()

    # ------------------
    # CHART 1: HISTORICAL CONTEXT (2 Years)
    # ------------------
    st.subheader("📊 Alpha Swarm Telemetry (Historical Context)")
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # 1. HISTORICAL CONE
    fig.add_trace(go.Scatter(x=full_data.index, y=lower_cone, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
    fig.add_trace(go.Scatter(x=full_data.index, y=upper_cone, fill='tonexty', fillcolor='rgba(0, 100, 255, 0.1)', 
                             line=dict(width=0), name="Hist. Cone", hoverinfo='skip'), row=1, col=1)

    # 2. PRICE
    fig.add_trace(go.Candlestick(x=full_data.index, 
                                 open=full_data['Open']['SPY'], high=full_data['High']['SPY'], 
                                 low=full_data['Low']['SPY'], close=full_data['Close']['SPY'], 
                                 name='SPY'), row=1, col=1)

    # 3. RED ZONES
    emergency_days = gov_df[gov_df['Level_7']].index
    for date in emergency_days:
        fig.add_vrect(x0=date - timedelta(hours=12), x1=date + timedelta(hours=12), 
                      fillcolor="red", opacity=0.1, layer="below", line_width=0, row=1, col=1)

    # 4. PPO
    fig.add_trace(go.Scatter(x=full_data.index, y=ppo, name="PPO Line", line=dict(color='cyan', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=full_data.index, y=sig, name="Signal", line=dict(color='orange', width=1)), row=2, col=1)
    colors = ['#00ff00' if val >= 0 else '#ff0000' for val in hist]
    fig.add_trace(go.Bar(x=full_data.index, y=hist, name="Histogram", marker_color=colors), row=2, col=1)

    fig.update_layout(height=500, template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
        plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font=dict(color='white'))
    
    st.plotly_chart(fig, use_container_width=True)

    # ------------------
    # CHART 2: TACTICAL ZOOM (Last 60 Days + 30 Day Forecast)
    # ------------------
    st.divider()
    st.subheader("🔭 Tactical Forecast (Zoom: Last 60 Days + Next 30 Days)")
    
    # Filter Data for Zoom (Last 60 Days)
    zoom_start = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    zoom_data = full_data[full_data.index >= zoom_start]
    zoom_upper = upper_cone[upper_cone.index >= zoom_start]
    zoom_lower = lower_cone[lower_cone.index >= zoom_start]
    
    fig2 = go.Figure()

    # 1. RECENT HISTORICAL CONE
    fig2.add_trace(go.Scatter(x=zoom_data.index, y=zoom_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig2.add_trace(go.Scatter(x=zoom_data.index, y=zoom_upper, fill='tonexty', fillcolor='rgba(0, 100, 255, 0.1)', 
                              line=dict(width=0), name="Hist. Cone", hoverinfo='skip'))

    # 2. FUTURE CONE (Purple)
    fig2.add_trace(go.Scatter(x=f_dates, y=f_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig2.add_trace(go.Scatter(x=f_dates, y=f_upper, fill='tonexty', fillcolor='rgba(200, 0, 255, 0.15)', 
                              line=dict(width=0), name="Proj. Uncertainty", hoverinfo='skip'))

    # 3. SWARM MEAN FORECAST
    fig2.add_trace(go.Scatter(x=f_dates, y=f_mean, name="Swarm Forecast", 
                              line=dict(color='white', width=2, dash='dot')))

    # 4. PRICE (Candles)
    fig2.add_trace(go.Candlestick(x=zoom_data.index, 
                                  open=zoom_data['Open']['SPY'], high=zoom_data['High']['SPY'], 
                                  low=zoom_data['Low']['SPY'], close=zoom_data['Close']['SPY'], 
                                  name='SPY'))

    fig2.update_layout(height=450, template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
        plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font=dict(color='white'),
        xaxis_rangeslider_visible=False) # Hide slider on zoom chart for cleanliness
    
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("🟪 Purple Area = 30-Day 'Headlights' (Projected Volatility Cone)")

    # ------------------
    # STRATEGIST CORNER
    # ------------------
    st.subheader("📝 Chief Strategist's View")
    with st.expander("Read Monthly Forecast (Feb 2026)", expanded=True):
        st.markdown("""
        **"The Hospital Patient"**
        *Viewed from 30,000 feet, the market should be zooming up... However, the market seems to be discounting the spending bonanza.*
        
        **Alpha Swarm Verification:**
        * **Governance:** The Breadth Ratio (RSP/SPY) is confirming the "anemic" weakness.
        * **Momentum:** The PPO Line is the key watch. If it crosses below Zero, the "Coma" deepens.
        """)

except Exception as e:
    st.error(f"Error loading data: {e}")