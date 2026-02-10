import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE SETUP (v16.3 - LIVE MONITOR FEED)
# ==========================================
st.set_page_config(page_title="Tiedeman Research | Alpha Swarm", page_icon="🛡️", layout="wide")

# SIDEBAR SETTINGS
with st.sidebar:
    st.header("🏛️ Tiedeman Research")

    # TOGGLE: Defaults to FALSE (Light Mode / High Contrast)
    dark_mode = st.toggle("Enable Dark Mode", value=False, help="Toggle between Institutional Dark Mode and Standard Light Mode.")
    
    st.divider()
    st.caption("Powered by Alpha Swarm v16.3")
    st.caption("Status: PROTOTYPE (May 2026 Target)")

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
    .stApp { background-color: #0E1117 !important; }
    
    /* MARKDOWN TEXT ONLY */
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
        color: #E6E6E6 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* HEADERS SPECIFIC */
    h1, h2, h3, h4, h5, h6 { color: #C6A87C !important; }
    
    /* METRICS */
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; }
    div[data-testid="stMetricDelta"] svg { fill: #00FF00 !important; }
    
    /* TABS */
    button[data-baseweb="tab"] { color: #586069; font-weight: bold; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #C6A87C !important; border-top-color: #C6A87C !important; background-color: #161B22; }

    /* TOOLTIPS (Question Marks) - Light Grey */
    [data-testid="stTooltipIcon"] { color: #AAAAAA !important; }

    /* MARKET GRID CARDS */
    .market-card {
        background-color: #161B22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #0D1117 !important; border-right: 1px solid #30363d; }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #C6A87C !important; }
    
    /* EXPANDER (READ FORECAST) - FIX WHITE ON WHITE */
    [data-testid="stExpander"] { 
        background-color: #161B22 !important; 
        border: 1px solid #30363d !important; 
        color: #E6E6E6 !important;
    }
    [data-testid="stExpander"] summary { color: #C6A87C !important; }
    
    /* PREMIUM COMPONENTS */
    .premium-banner {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white !important;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        border: 1px solid #4a90e2;
    }

    /* FOOTER */
    .custom-footer { font-size: 12px; color: #8b949e !important; text-align: center; margin-top: 50px; border-top: 1px solid #30363d; padding-top: 20px; }
    
    .big-badge {
        font-size: 20px; font-weight: bold; padding: 10px 20px;
        border-radius: 8px; text-align: center; margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2); color: #FFFFFF !important;
        text-transform: uppercase; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    chart_template = "plotly_dark"
    chart_bg = '#0E1117'
    chart_font_color = '#C6A87C'
    
else:
    # --- LIGHT MODE CSS (Boutique Financial - DEFAULT) ---
    st.markdown("""
    <style>
    /* HIDE STREAMLIT DEFAULT MENUS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* FORCE LIGHT GREY BACKGROUND */
    .stApp { background-color: #F0F2F6 !important; }
    
    /* MARKDOWN TEXT ONLY */
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
        color: #333333 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* HEADERS SPECIFIC */
    h1, h2, h3, h4, h5, h6 { color: #003366 !important; }
    
    /* METRICS */
    div[data-testid="stMetricValue"] { color: #003366 !important; font-weight: 700 !important; }

    /* MARKET GRID CARDS */
    .market-card {
        background-color: #FFFFFF;
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 10px;
    }

    /* TABS */
    button[data-baseweb="tab"] { color: #666; font-weight: bold; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #003366 !important; border-top-color: #003366 !important; background-color: #FFFFFF; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #ddd; }
    section[data-testid="stSidebar"] h2 { color: #003366 !important; }

    /* TOOLTIPS (Question Marks) - Light Grey */
    [data-testid="stTooltipIcon"] { color: #888888 !important; }

    /* EXPANDER (READ FORECAST) */
    [data-testid="stExpander"] { 
        background-color: #FFFFFF !important; 
        border: 1px solid #ddd !important; 
    }
    [data-testid="stExpander"] summary { color: #003366 !important; font-weight: 600 !important; }

    /* PREMIUM COMPONENTS */
    .premium-banner {
        background: linear-gradient(135deg, #003366 0%, #0055AA 100%);
        color: white !important;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* BADGE */
    .big-badge { 
        font-size: 20px; font-weight: bold; padding: 10px 20px;
        border-radius: 8px; text-align: center; margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); color: #FFFFFF !important;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .custom-footer { font-size: 12px; color: #666 !important; text-align: center; margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)
    
    chart_template = "plotly_white"
    chart_bg = '#F0F2F6'
    chart_font_color = '#003366'

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
st.title("🏛️ TIEDEMAN RESEARCH")
st.markdown("### Alpha Swarm Intelligence: Global Market Command Center")
st.caption(f"Governance Protocol Active: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

try:
    full_data = fetch_data()
    closes = full_data['Close']
    gov_df, status, color, reason = calculate_governance_history(full_data)
    
    # Pre-calculate active logic for monitor feed
    latest_monitor = gov_df.iloc[-1]
    
    # --- TAB NAVIGATION (The Boutique Touch) ---
    tab1, tab2, tab3 = st.tabs(["🚀 Market Swarm", "🛡️ Risk Governance", "📝 Strategist View"])

    # ---------------------------
    # TAB 1: MARKET SWARM
    # ---------------------------
    with tab1:
        st.subheader("Global Asset Grid")
        
        assets = [
            {"name": "Dow Jones", "ticker": "^DJI", "color": "#00CC00"},
            {"name": "S&P 500", "ticker": "SPY", "color": "#00CC00"},
            {"name": "Nasdaq", "ticker": "^IXIC", "color": "#00CC00"},
            {"name": "VIX Index", "ticker": "^VIX", "color": "#FF5500"},
            {"name": "Gold", "ticker": "GC=F", "color": "#FFD700"},
            {"name": "Crude Oil", "ticker": "CL=F", "color": "#888888"}
        ]
        
        c1, c2, c3 = st.columns(3)
        for i, col in enumerate([c1, c2, c3]):
            asset = assets[i]
            with col:
                series = closes[asset['ticker']].dropna()
                if not series.empty:
                    current = series.iloc[-1]; prev = series.iloc[-2]; delta = current - prev; pct = (delta / prev) * 100
                    delta_color = "#00CC00" if delta >= 0 else "#FF5500"

                    st.markdown(f"""
                    <div class="market-card">
                        <div style="font-size: 14px; opacity: 0.8; font-weight: bold;">{asset['name']}</div>
                        <div style="font-size: 22px; font-weight: bold; margin: 5px 0;">{current:,.2f}</div>
                        <div style="color: {delta_color}; font-size: 14px; font-weight: 600;">{delta:+.2f} ({pct:+.2f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(make_sparkline(series.tail(30), asset['color']), use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("---")
        
        c4, c5, c6 = st.columns(3)
        for i, col in enumerate([c4, c5, c6]):
            asset = assets[i+3]
            with col:
                series = closes[asset['ticker']].dropna()
                if not series.empty:
                    current = series.iloc[-1]; prev = series.iloc[-2]; delta = current - prev; pct = (delta / prev) * 100
                    delta_color = "#00CC00" if delta >= 0 else "#FF5500"

                    st.markdown(f"""
                    <div class="market-card">
                        <div style="font-size: 14px; opacity: 0.8; font-weight: bold;">{asset['name']}</div>
                        <div style="font-size: 22px; font-weight: bold; margin: 5px 0;">{current:,.2f}</div>
                        <div style="color: {delta_color}; font-size: 14px; font-weight: 600;">{delta:+.2f} ({pct:+.2f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(make_sparkline(series.tail(30), asset['color']), use_container_width=True, config={'displayModeBar': False})

        st.divider()

        # --- SWARM DEEP DIVE ---
        st.subheader("🔍 Swarm Deep Dive")
        spy_close = full_data['Close']['SPY']
        ppo, sig, hist = calculate_ppo(spy_close)
        sma, std, upper_cone, lower_cone = calculate_cone(spy_close)
        last_date = spy_close.index[-1]; last_val = spy_close.iloc[-1]; last_dev = std.iloc[-1]
        f_dates, f_mean, f_upper, f_lower = generate_forecast(last_date, last_val, last_dev, days=30)
        
        c1, c2 = st.columns(2)
        with c1: view_mode = st.radio("Select View Horizon:", ["Tactical (60-Day Zoom)", "Strategic (2-Year History)"], horizontal=True)
        with c2: st.radio("Market Scope (Premium):", ["US Market (Active)", "Global Swarm 🔒", "Sector Rotation 🔒"], index=0, horizontal=True, disabled=True, help="Institutional modules include Global Macro flows and Sector Rotation models.")

        if view_mode == "Tactical (60-Day Zoom)":
            start_filter = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'); show_forecast = True
        else:
            start_filter = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d'); show_forecast = False
            
        chart_data = full_data[full_data.index >= start_filter]
        chart_lower = lower_cone[lower_cone.index >= start_filter]
        chart_upper = upper_cone[upper_cone.index >= start_filter]

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_upper, fill='tonexty', fillcolor='rgba(0, 100, 255, 0.1)', line=dict(width=0), name="Fair Value Cone", hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Candlestick(x=chart_data.index, open=chart_data['Open']['SPY'], high=chart_data['High']['SPY'], low=chart_data['Low']['SPY'], close=chart_data['Close']['SPY'], name='SPY'), row=1, col=1)

        if show_forecast:
            fig.add_trace(go.Scatter(x=f_dates, y=f_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
            fig.add_trace(go.Scatter(x=f_dates, y=f_upper, fill='tonexty', fillcolor='rgba(200, 0, 255, 0.15)', line=dict(width=0), name="Proj. Uncertainty", hoverinfo='skip'), row=1, col=1)
            fig.add_trace(go.Scatter(x=f_dates, y=f_mean, name="Swarm Forecast", line=dict(color=chart_font_color, width=2, dash='dot')), row=1, col=1)

        if view_mode == "Strategic (2-Year History)":
            start_date = chart_data.index[0]; mask = (gov_df['Level_7']) & (gov_df.index >= start_date); emergency_days = gov_df.index[mask]
            for date in emergency_days: fig.add_vrect(x0=date - timedelta(hours=12), x1=date + timedelta(hours=12), fillcolor="red", opacity=0.1, layer="below", line_width=0, row=1, col=1)

        subset_ppo = ppo[ppo.index >= chart_data.index[0]]; subset_sig = sig[sig.index >= chart_data.index[0]]; subset_hist = hist[hist.index >= chart_data.index[0]]
        fig.add_trace(go.Scatter(x=chart_data.index, y=subset_ppo, name="Swarm Trend", line=dict(color='cyan', width=1)), row=2, col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=subset_sig, name="Signal", line=dict(color='orange', width=1)), row=2, col=1)
        colors = ['#00ff00' if val >= 0 else '#ff0000' for val in subset_hist]
        fig.add_trace(go.Bar(x=chart_data.index, y=subset_hist, name="Velocity", marker_color=colors), row=2, col=1)

        fig.update_layout(height=500, template=chart_template, margin=dict(l=0, r=0, t=0, b=0), showlegend=False, plot_bgcolor=chart_bg, paper_bgcolor=chart_bg, font=dict(color=chart_font_color), xaxis_rangeslider_visible=False)
        fig.update_xaxes(showgrid=False); fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        if show_forecast: st.caption("🟪 Purple Area = 30-Day 'Headlights' (Projected Volatility Cone)")
        
        st.markdown("""
        <div class="premium-banner">
        🔒 Institutional Access Required: Unlock Sector Rotation & Global Flows
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------
    # TAB 2: GOVERNANCE
    # ---------------------------
    with tab2:
        st.subheader("🛡️ Risk Governance & Compliance")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f'<div class="big-badge" style="background-color: {color}; border: 2px solid {color}; box-shadow: 0 0 15px {color}; text-shadow: 1px 1px 2px black;">GOVERNANCE STATUS: {status}</div>', unsafe_allow_html=True)
            st.caption(f"Reason: {reason}")
        with col2:
            latest_vix = full_data['Close']['^VIX'].iloc[-1]
            st.metric("Risk (VIX)", f"{latest_vix:.2f}", delta_color="inverse")

        st.subheader("⏱️ Tactical Horizons")
        h1, h2, h3 = st.columns(3)
        with h1: st.info("**1 WEEK (Momentum)**"); st.markdown("🟢 **RISING**" if hist.iloc[-1] > 0 else "🔴 **WEAKENING**")
        with h2: st.info("**1 MONTH (Trend)**"); st.markdown("🟢 **BULLISH**" if ppo.iloc[-1] > 0 else "🔴 **BEARISH**")
        with h3: st.info("**6 MONTH (Structural)**"); st.markdown("🟢 **SAFE**" if status == "NORMAL OPS" else f"🔴 **{status}**")

        st.divider()
        st.subheader("📡 Active Monitor Feed (Live Logic)")
        
        # Replace the raw Code Block with a "Live Monitor Dashboard"
        m1, m2, m3 = st.columns(3)
        
        # Monitor 1: Credit Spreads (HYG vs IEF)
        # Logic: If HYG falls faster than IEF, Credit Spreads are widening (Bad)
        credit_val = latest_monitor['Credit_Delta']
        credit_status = "STRESS" if credit_val < -0.015 else "NOMINAL"
        m1.metric("Credit Spreads (HYG/IEF)", f"{credit_val:.2%}", 
                 delta="STABLE" if credit_status=="NOMINAL" else "WIDENING", 
                 delta_color="normal" if credit_status=="NOMINAL" else "inverse",
                 help="Tracks High Yield bonds vs Treasuries. Widening spreads indicate banking stress.")

        # Monitor 2: US Dollar (DXY)
        # Logic: Fast spike in DXY kills earnings
        dxy_val = latest_monitor['DXY_Delta']
        dxy_status = "SPIKE" if dxy_val > 0.02 else "STABLE"
        m2.metric("US Dollar (DXY)", f"{dxy_val:.2%}", 
                 delta="STABLE" if dxy_status=="STABLE" else "SPIKING", 
                 delta_color="inverse",
                 help="Tracks value of USD. Rapid spikes (>2%) hurt multinational earnings.")

        # Monitor 3: Market Breadth (RSP vs SPY)
        # Logic: If Equal Weight (RSP) lags Cap Weight (SPY), the rally is thinning (Bad)
        breadth_val = latest_monitor['Breadth_Delta']
        breadth_status = "NARROWING" if breadth_val < -0.025 else "HEALTHY"
        m3.metric("Market Breadth (RSP/SPY)", f"{breadth_val:.2%}", 
                 delta=breadth_status, 
                 delta_color="normal" if breadth_status=="HEALTHY" else "inverse",
                 help="Compares Equal Weight S&P to Cap Weight. Narrowing breadth warns of a top.")

    # ---------------------------
    # TAB 3: STRATEGIST VIEW
    # ---------------------------
    with tab3:
        st.subheader("📝 Tiedeman Research: Chief Strategist's View")
        
        try:
            # ------------------------------------------------------------------
            # PASTE YOUR GOOGLE SHEET "PUBLISH TO WEB" CSV LINK BELOW
            # ------------------------------------------------------------------
            SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4ik-SBHr_ER_SyMHgwVAds3UaxRtPTA426qU_26TuHkHlyb5h6zl8_H9E-_Kw5FUO3W1mBU8CKiZP/pub?gid=0&single=true&output=csv" 
            
            # Logic to handle both local file (backup) and live sheet
            if "INSERT_YOUR" in SHEET_URL:
                # Fallback to local file if user hasn't pasted link yet
                update_df = pd.read_csv("data/update.csv")
            else:
                # Live Google Sheet Connection
                update_df = pd.read_csv(SHEET_URL)
                
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
            up_text = "Strategist update pending connection."

        with st.expander(f"Read Forecast ({up_date})", expanded=True):
            st.markdown(f'**"{up_title}"**')
            st.markdown(up_text)
            
        st.info("💡 **Analyst Note:** This commentary is pulled live from the Chief Strategist's desk via the Alpha Swarm CMS.")

    # FOOTER
    st.markdown("""
    <div class="custom-footer">
    TIEDEMAN RESEARCH | ALPHA SWARM PROTOCOL v16.3 | INSTITUTIONAL RISK GOVERNANCE<br>
    Disclaimer: This tool provides market analysis for informational purposes only. Not financial advice.<br>
    <br>
    <strong>Institutional Access:</strong> <a href="mailto:institutional@tiedeman.com" style="color: inherit; text-decoration: none; font-weight: bold;">institutional@tiedeman.com</a>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading data: {e}")