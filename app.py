import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE SETUP (v14.0 - FINAL CODE FREEZE)
# ==========================================
st.set_page_config(page_title="Alpha Swarm", page_icon="🛡️", layout="wide")

# SIDEBAR SETTINGS
with st.sidebar:
    st.header("⚙️ Settings")
    dark_mode = st.toggle("Enable Dark Mode", value=False, help="Toggle between Institutional Dark Mode and Standard Light Mode.")
    st.divider()
    st.caption("Alpha Swarm v14.0")

# CONDITIONAL CSS LOGIC
if dark_mode:
    # --- DARK MODE CSS (Institutional) ---
    st.markdown("""
    <style>
    /* HIDE STREAMLIT DEFAULT MENUS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* GLOBAL BACKGROUND */
    .stApp { background-color: #000000; }
    
    /* TEXT & HEADERS */
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }
    p, li, span, div { color: #E0E0E0; }
    
    /* METRICS */
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; }
    div[data-testid="stMetricDelta"] svg { fill: #00FF00 !important; }
    
    /* MARKET GRID CARDS */
    .market-card {
        background-color: #161b22;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #0e1117 !important; }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #888888 !important; }
    
    /* COMPONENTS */
    div[data-testid="stRadio"] > label { color: #FFFFFF !important; font-weight: bold; }
    [data-testid="stExpander"] { background-color: #161b22 !important; border: 1px solid #30363d !important; }
    [data-testid="stExpander"] summary { color: #ffffff !important; }
    
    /* FOOTER */
    .custom-footer { font-size: 12px; color: #666 !important; text-align: center; margin-top: 50px; }
    .big-badge { font-size: 24px; font-weight: bold; padding: 15px; border-radius: 5px; text-align: center; margin-bottom: 20px; border: 1px solid #333; color: #FFFFFF !important;}
    </style>
    """, unsafe_allow_html=True)
    
    chart_template = "plotly_dark"
    chart_bg = '#0E1117'
    chart_font_color = 'white'
    
else:
    # --- LIGHT MODE CSS (MarketWatch Style) ---
    st.markdown("""
    <style>
    /* HIDE STREAMLIT DEFAULT MENUS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TEXT & HEADERS */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, p, li, span, div { 
        color: #000000 !important; 
    }
    
    /* METRICS */
    div[data-testid="stMetricValue"] { color: #000000 !important; font-weight: 700 !important; }
    
    /* BADGE */
    .big-badge { 
        font-size: 24px; font-weight: bold; padding: 15px; 
        border-radius: 5px; text-align: center; margin-bottom: 20px; 
        border: 2px solid #000; color: #000 !important;
    }
    .custom-footer { font-size: 12px; color: #333 !important; text-align: center; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)
    
    chart_template = "plotly_white"
    chart_bg = '#FFFFFF'
    chart_font_color = 'black'

# ==========================================
# 2. THE ENGINE
# ==========================================
@st.cache_data(ttl=3600)
def fetch_data():
    with st.spinner('Accessing Global Market Data...'):
        tickers = ["SPY", "^DJI", "^IXIC", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB", "GC=F", "CL=F"]
        start = (datetime.now() - timedelta(days=1825)).strftime('%Y-%m-%d')
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

def make_sparkline(data, color):
    # Helper to create those mini MarketWatch charts
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', 
                            line=dict(color=color, width=2), hoverinfo='skip'))
    fig.update_layout(
        height=50, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# ==========================================
# 3. THE UI RENDER
# ==========================================
st.title("🛡️ ALPHA SWARM GOVERNANCE")
st.markdown("### Global Market Command Center")
st.caption(f"Data Feed Active: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

try:
    full_data = fetch_data()
    closes = full_data['Close']
    gov_df, status, color, reason = calculate_governance_history(full_data)
    
    # =============================================
    # SECTION 1: MARKETWATCH GRID
    # =============================================
    
    assets = [
        {"name": "Dow Jones", "ticker": "^DJI", "color": "#00CC00"},
        {"name": "S&P 500", "ticker": "SPY", "color": "#00CC00"},
        {"name": "Nasdaq", "ticker": "^IXIC", "color": "#00CC00"},
        {"name": "VIX Index", "ticker": "^VIX", "color": "#FF5500"},
        {"name": "Gold", "ticker": "GC=F", "color": "#FFD700"},
        {"name": "Crude Oil", "ticker": "CL=F", "color": "#888888"}
    ]
    
    # Row 1
    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]
    
    for i in range(3):
        asset = assets[i]
        with cols[i]:
            series = closes[asset['ticker']].dropna()
            if not series.empty:
                current = series.iloc[-1]
                prev = series.iloc[-2]
                delta = current - prev
                pct = (delta / prev) * 100
                st.metric(asset['name'], f"{current:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
                spark = make_sparkline(series.tail(30), asset['color'])
                st.plotly_chart(spark, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    
    # Row 2
    c4, c5, c6 = st.columns(3)
    cols2 = [c4, c5, c6]
    
    for i in range(3):
        asset = assets[i+3]
        with cols2[i]:
            series = closes[asset['ticker']].dropna()
            if not series.empty:
                current = series.iloc[-1]
                prev = series.iloc[-2]
                delta = current - prev
                pct = (delta / prev) * 100
                st.metric(asset['name'], f"{current:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
                spark = make_sparkline(series.tail(30), asset['color'])
                st.plotly_chart(spark, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # =============================================
    # SECTION 2: THE SWARM DEEP DIVE
    # =============================================
    
    st.subheader("🔍 Swarm Deep Dive") # UPDATED: Removed (SPY)
    
    spy_close = full_data['Close']['SPY']
    ppo, sig, hist = calculate_ppo(spy_close)
    sma, std, upper_cone, lower_cone = calculate_cone(spy_close)
    
    last_date = spy_close.index[-1]
    last_val = spy_close.iloc[-1]
    last_dev = std.iloc[-1]
    f_dates, f_mean, f_upper, f_lower = generate_forecast(last_date, last_val, last_dev, days=30)
    
    # CHART CONTROLS
    c1, c2 = st.columns(2)
    with c1:
        view_mode = st.radio("Select View Horizon:", 
                             ["Tactical (60-Day Zoom)", "Strategic (2-Year History)"], 
                             horizontal=True)
    with c2:
        st.radio("Market Scope (Premium):", ["US Market (Active)", "Global Swarm 🔒", "Sector Rotation 🔒"], 
                 index=0, horizontal=True, disabled=True)

    # PREPARE DATA
    if view_mode == "Tactical (60-Day Zoom)":
        start_filter = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        chart_data = full_data[full_data.index >= start_filter]
        chart_lower = lower_cone[lower_cone.index >= start_filter]
        chart_upper = upper_cone[upper_cone.index >= start_filter]
        show_forecast = True
    else: # Strategic
        start_filter = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        chart_data = full_data[full_data.index >= start_filter]
        chart_lower = lower_cone[lower_cone.index >= start_filter]
        chart_upper = upper_cone[upper_cone.index >= start_filter]
        show_forecast = False

    # BUILD CHART
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.7, 0.3])

    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_upper, fill='tonexty', fillcolor='rgba(0, 100, 255, 0.1)', 
                             line=dict(width=0), name="Fair Value Cone", hoverinfo='skip'), row=1, col=1)

    fig.add_trace(go.Candlestick(x=chart_data.index, 
                                 open=chart_data['Open']['SPY'], high=chart_data['High']['SPY'], 
                                 low=chart_data['Low']['SPY'], close=chart_data['Close']['SPY'], 
                                 name='SPY'), row=1, col=1)

    if show_forecast:
        fig.add_trace(go.Scatter(x=f_dates, y=f_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=f_dates, y=f_upper, fill='tonexty', fillcolor='rgba(200, 0, 255, 0.15)', 
                                 line=dict(width=0), name="Proj. Uncertainty", hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=f_dates, y=f_mean, name="Swarm Forecast", 
                                 line=dict(color=chart_font_color, width=2, dash='dot')), row=1, col=1)

    if view_mode == "Strategic (2-Year History)":
        start_date = chart_data.index[0]
        mask = (gov_df['Level_7']) & (gov_df.index >= start_date)
        emergency_days = gov_df.index[mask]
        for date in emergency_days:
            fig.add_vrect(x0=date - timedelta(hours=12), x1=date + timedelta(hours=12), 
                          fillcolor="red", opacity=0.1, layer="below", line_width=0, row=1, col=1)

    subset_ppo = ppo[ppo.index >= chart_data.index[0]]
    subset_sig = sig[sig.index >= chart_data.index[0]]
    subset_hist = hist[hist.index >= chart_data.index[0]]
    
    fig.add_trace(go.Scatter(x=chart_data.index, y=subset_ppo, name="Swarm Trend", line=dict(color='cyan', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=chart_data.index, y=subset_sig, name="Signal", line=dict(color='orange', width=1)), row=2, col=1)
    colors = ['#00ff00' if val >= 0 else '#ff0000' for val in subset_hist]
    fig.add_trace(go.Bar(x=chart_data.index, y=subset_hist, name="Velocity", marker_color=colors), row=2, col=1)

    # LAYOUT (UPDATED: MODEBAR REMOVED)
    fig.update_layout(height=500, template=chart_template, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
        plot_bgcolor=chart_bg, paper_bgcolor=chart_bg, font=dict(color=chart_font_color), xaxis_rangeslider_visible=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    if show_forecast:
        st.caption("🟪 Purple Area = 30-Day 'Headlights' (Projected Volatility Cone)")

    st.divider()

    # =============================================
    # SECTION 3: GOVERNANCE & BADGES
    # =============================================
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div class="big-badge" style="background-color: {color}; color: white;">GOVERNANCE STATUS: {status}</div>', unsafe_allow_html=True)
        st.caption(f"Reason: {reason}")
    with col2:
        latest_vix = full_data['Close']['^VIX'].iloc[-1]
        st.metric("Risk (VIX)", f"{latest_vix:.2f}", delta_color="inverse")

    st.subheader("⏱️ Tactical Horizons")
    h1, h2, h3 = st.columns(3)
    with h1:
        st.info("**1 WEEK (Momentum)**")
        st.markdown("🟢 **RISING**" if hist.iloc[-1] > 0 else "🔴 **WEAKENING**")
    with h2:
        st.info("**1 MONTH (Trend)**")
        st.markdown("🟢 **BULLISH**" if ppo.iloc[-1] > 0 else "🔴 **BEARISH**")
    with h3:
        st.info("**6 MONTH (Structural)**")
        st.markdown("🟢 **SAFE**" if status == "NORMAL OPS" else f"🔴 **{status}**")
        
    st.divider()

    # =============================================
    # SECTION 4: STRATEGIST VIEW
    # =============================================
    st.subheader("📝 Chief Strategist's View")
    
    try:
        update_df = pd.read_csv("update.csv")
        update_data = dict(zip(update_df['Key'], update_df['Value']))
        
        up_date = update_data.get('Date', 'Current')
        up_title = update_data.get('Title', 'Market Update')
        raw_text = str(update_data.get('Text', 'Monitoring market conditions...'))
        raw_text = raw_text.replace("\\n", "\n")
        lines = [line.strip() for line in raw_text.split('\n')]
        up_text = '\n\n'.join(lines)
        
    except Exception:
        up_date = "System Status"
        up_title = "Data Feed Offline"
        up_text = "Strategist update pending."

    with st.expander(f"Read Forecast ({up_date})", expanded=True):
        st.markdown(f'**"{up_title}"**')
        st.markdown(up_text)

    # FOOTER
    st.markdown("""
    <div class="custom-footer">
    ALPHA SWARM v14.0 (MARKETWATCH GRID EDITION) | INSTITUTIONAL RISK GOVERNANCE<br>
    Disclaimer: This tool provides market analysis for informational purposes only. Not financial advice.
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading data: {e}")