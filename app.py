import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE SETUP (v12.1 - DEFAULT LIGHT MODE)
# ==========================================
st.set_page_config(page_title="Alpha Swarm", page_icon="🛡️", layout="wide")

# SIDEBAR SETTINGS
with st.sidebar:
    st.header("⚙️ Settings")
    # CHANGED: 'value' is now False to default to Light Mode
    dark_mode = st.toggle("Enable Dark Mode", value=False, help="Toggle between Institutional Dark Mode and Standard Light Mode.")
    st.divider()
    st.caption("Alpha Swarm v12.1")

# CONDITIONAL CSS LOGIC
if dark_mode:
    # --- DARK MODE CSS (Institutional High Contrast) ---
    st.markdown("""
    <style>
    /* 1. GLOBAL BACKGROUND */
    .stApp { background-color: #000000; }
    
    /* 2. HEADERS & TITLES (Force Bright White) */
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }
    
    /* 3. BODY TEXT (Force Light Grey) */
    p, li, span, div { color: #E0E0E0; }
    
    /* 4. RADIO BUTTONS & LABELS (Force Bright) */
    div[data-testid="stRadio"] > label { 
        color: #FFFFFF !important; 
        font-weight: bold;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        color: #E0E0E0 !important;
    }
    
    /* 5. CAPTIONS (Force Visible Grey) */
    div[data-testid="stCaptionContainer"] {
        color: #CCCCCC !important;
    }
    
    /* 6. METRIC LABELS ("VIX Level") */
    div[data-testid="stMetricLabel"] {
        color: #CCCCCC !important;
    }
    div[data-testid="stMetricValue"] { color: #00FF00 !important; }
    
    /* 7. EXPANDER & TOOLTIPS */
    [data-testid="stExpander"], div[data-testid="stTooltipContent"] {
        background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 6px;
    }
    [data-testid="stExpander"] summary { background-color: #161b22 !important; color: #ffffff !important; }
    [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary span { color: #ffffff !important; }
    [data-testid="stTooltipHoverTarget"] svg { fill: #FFFFFF !important; }
    
    /* 8. SIDEBAR (Keep Dimmed) */
    section[data-testid="stSidebar"] { background-color: #0e1117 !important; }
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label { color: #888888 !important; }
    
    /* 9. DISABLED OPTIONS */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[disabled] { 
        color: #666666 !important; 
        opacity: 0.5; cursor: not-allowed; 
    }
    
    /* 10. BADGE & FOOTER */
    .big-badge { font-size: 24px; font-weight: bold; padding: 15px; border-radius: 5px; text-align: center; margin-bottom: 20px; border: 1px solid #333; color: #FFFFFF !important;}
    .footer { font-size: 12px; color: #666 !important; text-align: center; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)
    
    chart_template = "plotly_dark"
    chart_bg = '#0E1117'
    chart_font_color = 'white'
    
else:
    # --- LIGHT MODE CSS (Clean Black/White) ---
    st.markdown("""
    <style>
    /* 1. FORCE DARKER TEXT */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
    .stApp p, .stApp li, .stApp span, .stApp div { 
        color: #000000 !important; 
    }
    
    /* 2. FORCE RADIO BUTTONS BLACK */
    div[data-testid="stRadio"] > label { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* 3. CAPTIONS & METRICS BLACK */
    div[data-testid="stCaptionContainer"] { color: #000000 !important; opacity: 1 !important; font-weight: 600 !important; }
    div[data-testid="stMetricLabel"] { color: #000000 !important; font-weight: bold !important; }
    
    /* 4. DISABLED OPTIONS */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[disabled] { 
        color: #666666 !important; opacity: 0.7; 
    }
    
    /* 5. BADGE STYLE */
    .big-badge { 
        font-size: 24px; font-weight: bold; padding: 15px; 
        border-radius: 5px; text-align: center; margin-bottom: 20px; 
        border: 2px solid #000; color: #000 !important;
    }
    .footer { font-size: 12px; color: #333 !important; text-align: center; margin-top: 50px; }
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
    with st.spinner('Downloading Market Data from Yahoo Finance...'):
        tickers = ["SPY", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB"]
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

# ==========================================
# 3. THE UI RENDER
# ==========================================
st.title("🛡️ ALPHA SWARM GOVERNANCE")
st.markdown("### Live Structural Risk & Momentum Monitor")
st.caption(f"Market Data valid as of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    
    # =============================================
    # SECTION 1: THE CHARTS
    # =============================================
    
    # CHART CONTROLS
    c1, c2 = st.columns(2)
    with c1:
        view_mode = st.radio("Select View Horizon:", 
                             ["Tactical (60-Day Zoom)", "Strategic (2-Year History)"], 
                             horizontal=True,
                             help="Toggle between short-term momentum (Tactical) and long-term structural trends (Strategic).")
    with c2:
        st.radio("Market Scope (Premium):", ["US Market (Active)", "Global Swarm 🔒", "Sector Rotation 🔒"], 
                 index=0, horizontal=True, disabled=True,
                 help="Global Swarm and Sector Rotation models are available to Institutional Tier subscribers.")

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

    # 1. CONE
    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_upper, fill='tonexty', fillcolor='rgba(0, 100, 255, 0.1)', 
                             line=dict(width=0), name="Fair Value Cone", hoverinfo='skip'), row=1, col=1)

    # 2. PRICE
    fig.add_trace(go.Candlestick(x=chart_data.index, 
                                 open=chart_data['Open']['SPY'], high=chart_data['High']['SPY'], 
                                 low=chart_data['Low']['SPY'], close=chart_data['Close']['SPY'], 
                                 name='SPY'), row=1, col=1)

    # 3. FORECAST
    if show_forecast:
        fig.add_trace(go.Scatter(x=f_dates, y=f_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=f_dates, y=f_upper, fill='tonexty', fillcolor='rgba(200, 0, 255, 0.15)', 
                                 line=dict(width=0), name="Proj. Uncertainty", hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=f_dates, y=f_mean, name="Swarm Forecast", 
                                 line=dict(color=chart_font_color, width=2, dash='dot')), row=1, col=1)

    # 4. RED ZONES
    if view_mode == "Strategic (2-Year History)":
        start_date = chart_data.index[0]
        mask = (gov_df['Level_7']) & (gov_df.index >= start_date)
        emergency_days = gov_df.index[mask]
        for date in emergency_days:
            fig.add_vrect(x0=date - timedelta(hours=12), x1=date + timedelta(hours=12), 
                          fillcolor="red", opacity=0.1, layer="below", line_width=0, row=1, col=1)

    # 5. MOMENTUM
    subset_ppo = ppo[ppo.index >= chart_data.index[0]]
    subset_sig = sig[sig.index >= chart_data.index[0]]
    subset_hist = hist[hist.index >= chart_data.index[0]]
    
    fig.add_trace(go.Scatter(x=chart_data.index, y=subset_ppo, name="Swarm Trend", line=dict(color='cyan', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=chart_data.index, y=subset_sig, name="Signal", line=dict(color='orange', width=1)), row=2, col=1)
    colors = ['#00ff00' if val >= 0 else '#ff0000' for val in subset_hist]
    fig.add_trace(go.Bar(x=chart_data.index, y=subset_hist, name="Velocity", marker_color=colors), row=2, col=1)

    # LAYOUT (Dynamic Theme Applied)
    fig.update_layout(height=500, template=chart_template, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
        plot_bgcolor=chart_bg, paper_bgcolor=chart_bg, font=dict(color=chart_font_color), xaxis_rangeslider_visible=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)
    
    if show_forecast:
        st.caption("🟪 Purple Area = 30-Day 'Headlights' (Projected Volatility Cone)")

    st.divider()

    # =============================================
    # SECTION 2: GOVERNANCE & BADGES
    # =============================================
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div class="big-badge" style="background-color: {color}; color: white;">GOVERNANCE STATUS: {status}</div>', unsafe_allow_html=True)
        st.caption(f"Reason: {reason}")
    with col2:
        latest_vix = full_data['Close']['^VIX'].iloc[-1]
        st.metric("VIX Level", f"{latest_vix:.2f}", delta_color="inverse")

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
    # SECTION 3: STRATEGIST VIEW
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
    <div class="footer">
    ALPHA SWARM v1.0 (BETA) | INSTITUTIONAL RISK GOVERNANCE<br>
    Disclaimer: This tool provides market analysis for informational purposes only. Not financial advice.
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading data: {e}")