import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE SETUP (v18.0 - BRUSHED STEEL & GOLD)
# ==========================================
st.set_page_config(page_title="MacroEffects | Global Command", page_icon="M", layout="wide")

# SIDEBAR SETTINGS
with st.sidebar:
    st.header("M | MacroEffects")
    st.divider()
    st.caption("Powered by Alpha Swarm v18.0")
    st.caption("Status: INSTITUTIONAL ACCESS")
    st.divider()
    dark_mode = st.toggle("Dark Mode", value=False)

# THEME CONFIGURATION
theme_config = {
    True: { # Dark Mode
        "bg_color": "#0e1117",
        "card_bg": "rgba(22, 27, 34, 0.7)",
        "card_border": "1px solid rgba(255, 255, 255, 0.08)",
        "text_primary": "#e6e6e6",
        "text_secondary": "#8b949e",
        "accent_gold": "#C6A87C",
        "accent_blue": "#00f2ff",
        "glass_shadow": "0 4px 30px rgba(0, 0, 0, 0.3)",
        "sidebar_bg": "#090c10",
        "sidebar_border": "#30363d",
        "chart_template": "plotly_dark",
        "chart_font_color": "#e6e6e6",
        "glass_bg": "rgba(255, 255, 255, 0.05)",
        "steel_gradient": "linear-gradient(180deg, #E6E6E6 0%, #A4A4A4 48%, #E6E6E6 50%, #B8B8B8 100%)"
    },
    False: { # Light Mode
        "bg_color": "#ffffff",
        "card_bg": "rgba(255, 255, 255, 0.9)",
        "card_border": "1px solid rgba(49, 51, 63, 0.1)",
        "text_primary": "#31333F",
        "text_secondary": "#555555",
        "accent_gold": "#b08d55",
        "accent_blue": "#007bff",
        "glass_shadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
        "sidebar_bg": "#f8f9fa",
        "sidebar_border": "#dee2e6",
        "chart_template": "plotly_white",
        "chart_font_color": "#31333F",
        "glass_bg": "rgba(0, 0, 0, 0.05)",
        "steel_gradient": "linear-gradient(180deg, #555555 0%, #222222 48%, #555555 50%, #333333 100%)"
    }
}
current_theme = theme_config[dark_mode]

# --- INSTITUTIONAL VISUAL ARCHITECTURE ---
st.markdown(f"""
<style>
/* FONT IMPORTS */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Fira+Code:wght@300;500;700&display=swap');

/* GLOBAL VARIABLES */
:root {{
    --bg-color: {current_theme['bg_color']};
    --card-bg: {current_theme['card_bg']};
    --card-border: {current_theme['card_border']};
    --text-primary: {current_theme['text_primary']};
    --text-secondary: {current_theme['text_secondary']};
    --accent-gold: {current_theme['accent_gold']};
    --steel-gradient: {current_theme['steel_gradient']};
}}

/* TIGHTEN SPACING */
.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
}}

/* HIDE DEFAULT ELEMENTS */
#MainMenu {{visibility: visible;}}
footer {{visibility: hidden;}}
header {{visibility: visible;}}

/* --- THE STEEL HEADER ARCHITECTURE (Title & Subheaders) --- */
.steel-header {{
    background: linear-gradient(145deg, #1a1f26, #2d343f);
    padding: 15px 25px;
    border-radius: 8px;
    border: 1px solid #4a4f58;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

/* BRUSHED STEEL TEXT EFFECT */
.steel-text {{
    background: linear-gradient(180deg, #FFFFFF 0%, #A0A0A0 50%, #E0E0E0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 0;
}}

/* Title Size */
.steel-header h1 {{
    font-size: 32px !important; 
    margin: 0 !important;
    padding: 0 !important;
    background: linear-gradient(180deg, #FFFFFF 0%, #A0A0A0 50%, #E0E0E0 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}}

/* Subheader Size */
.steel-subheader {{
    font-size: 18px !important;
}}

/* APP BACKGROUND */
.stApp {{
    background-color: var(--bg-color) !important;
    font-family: 'Inter', sans-serif;
}}

/* TAB STYLING (Gradient Shading, No Icons) */
button[data-baseweb="tab"] {{
    background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.05) 100%) !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
    border-radius: 6px 6px 0 0 !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 14px;
    text-transform: uppercase;
    padding: 10px 20px;
    margin-right: 4px;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    background: linear-gradient(180deg, #2d343f 0%, #1a1f26 100%) !important;
    color: white !important;
    border-top: 2px solid var(--accent-gold) !important;
}}

/* GOLD PLAQUE (For Premium Radio) */
/* Targeted CSS for the Radio Button Container in the Swarm Deep Dive */
div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stRadio"] {
    background: linear-gradient(135deg, #bf953f 0%, #fcf6ba 25%, #b38728 50%, #fbf5b7 75%, #aa771c 100%);
    padding: 15px;
    border-radius: 8px;
    border: 2px solid #8a6e2f;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

/* Force Text in Gold Plaque to be Dark/Bold for Readability */
div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stRadio"] label p {
    color: #3b2c00 !important;
    font-weight: 800 !important;
    text-shadow: 0px 1px 0px rgba(255,255,255,0.4);
}

/* MINI GOVERNANCE BADGE */
.mini-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    font-weight: bold;
    color: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    margin-left: 10px;
    vertical-align: middle;
}

/* MARKET CARDS */
.market-card {
    background: var(--card-bg);
    border: var(--card-border);
    border-radius: 6px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 10px;
}
.market-ticker { color: var(--text-secondary); font-size: 11px; margin-bottom: 2px; }
.market-price { color: {current_theme['text_primary']}; font-family: 'Fira Code', monospace; font-size: 22px; font-weight: 700; margin: 2px 0; }
.market-delta { font-family: 'Fira Code', monospace; font-size: 13px; font-weight: 600; }

/* BIG BADGE (Tab 2) */
.big-badge {
    font-family: 'Inter', sans-serif;
    font-size: 18px;
    font-weight: 800;
    padding: 15px 25px;
    border-radius: 4px;
    text-align: center;
    margin-bottom: 20px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: white;
}

/* FOOTER */
.custom-footer {
    font-family: 'Fira Code', monospace;
    font-size: 10px;
    color: #484f58 !important;
    text-align: center;
    margin-top: 50px;
    border-top: 1px solid #30363d;
    padding-top: 20px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

chart_template = current_theme['chart_template']
chart_bg = 'rgba(0,0,0,0)'
chart_font_color = current_theme['chart_font_color']

# ==========================================
# 2. DATA ENGINE (Called Early for Header Badge)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_data():
    with st.spinner('Accessing Global Market Data...'):
        tickers = ["SPY", "^DJI", "^IXIC", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB", "GC=F", "CL=F"]
        start = (datetime.now() - timedelta(days=1825)).strftime('%Y-%m-%d')
        data = yf.download(tickers, start=start, progress=False)
    return data

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
    if latest['Level_7']: status, color, reason = "EMERGENCY", "#f93e3e", "Structural/Policy Failure"
    elif latest['Level_5']: status, color, reason = "CAUTION", "#ffaa00", "Market Divergence"
    elif latest['Level_4']: status, color, reason = "WATCHLIST", "#f1c40f", "Elevated Risk Monitors"
    else: status, color, reason = "NORMAL OPS", "#00d26a", "System Integrity Nominal"
        
    return df, status, color, reason

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

def make_sparkline(data, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', 
                            line=dict(color=color, width=2), hoverinfo='skip'))
    fig.update_layout(
        height=40, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# ==========================================
# 3. DATA FETCHING & STATUS PRE-CALC
# ==========================================
try:
    full_data = fetch_data()
    closes = full_data['Close']
    gov_df, status, color, reason = calculate_governance_history(full_data)
    latest_monitor = gov_df.iloc[-1]
except Exception as e:
    status, color, reason = "OFFLINE", "#888888", "Data connection failed"
    full_data = None

# ==========================================
# 4. THE UI RENDER
# ==========================================
# MAIN TITLE BAR (Steel Gradient)
st.markdown(f"""
<div class="steel-header">
    <h1>MacroEffects</h1>
    <div style="text-align: right;">
        <span style="font-size: 24px; color: #C6A87C;">☰</span>
    </div>
</div>
""", unsafe_allow_html=True)

# SUBHEADER WITH MINI-BADGE
st.markdown(f"""
<div style="margin-bottom: 20px;">
    <span style="font-family: 'Inter'; font-weight: 600; font-size: 16px; color: var(--text-secondary);">Macro-Economic Intelligence: Global Market Command Center</span>
    <div class="mini-badge" style="background-color: {color};">{status}</div>
</div>
""", unsafe_allow_html=True)

st.divider()

if full_data is not None:
    # --- TAB NAVIGATION (Gradient Backgrounds) ---
    tab1, tab2, tab3 = st.tabs(["Market Swarm", "Risk Governance", "Strategist View"])

    # ---------------------------
    # TAB 1: MARKET SWARM
    # ---------------------------
    with tab1:
        st.markdown('<div class="steel-header"><span class="steel-text steel-subheader">Global Asset Grid</span></div>', unsafe_allow_html=True)
        
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
                    delta_color = "#00d26a" if delta >= 0 else "#f93e3e"

                    st.markdown(f"""
                    <div class="market-card">
                        <div class="market-ticker">{asset['name']}</div>
                        <div class="market-price">{current:,.2f}</div>
                        <div class="market-delta" style="color: {delta_color};">{delta:+.2f} ({pct:+.2f}%)</div>
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
                    delta_color = "#00d26a" if delta >= 0 else "#f93e3e"

                    st.markdown(f"""
                    <div class="market-card">
                        <div class="market-ticker">{asset['name']}</div>
                        <div class="market-price">{current:,.2f}</div>
                        <div class="market-delta" style="color: {delta_color};">{delta:+.2f} ({pct:+.2f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(make_sparkline(series.tail(30), asset['color']), use_container_width=True, config={'displayModeBar': False})

        st.divider()

        # --- SWARM DEEP DIVE (Steel Header) ---
        st.markdown('<div class="steel-header"><span class="steel-text steel-subheader">Swarm Deep Dive</span></div>', unsafe_allow_html=True)
        
        spy_close = full_data['Close']['SPY']
        ppo, sig, hist = calculate_ppo(spy_close)
        sma, std, upper_cone, lower_cone = calculate_cone(spy_close)
        last_date = spy_close.index[-1]; last_val = spy_close.iloc[-1]; last_dev = std.iloc[-1]
        f_dates, f_mean, f_upper, f_lower = generate_forecast(last_date, last_val, last_dev, days=30)
        
        c1, c2 = st.columns(2)
        with c1: 
            view_mode = st.radio("Select View Horizon:", ["Tactical (60-Day Zoom)", "Strategic (2-Year History)"], horizontal=True)
        with c2: 
            # THE GOLD PLAQUE EFFECT
            st.radio("Market Scope (Premium):", ["US Market (Active)", "Global Swarm 🔒", "Sector Rotation 🔒"], index=0, horizontal=True, disabled=True)

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
        st.markdown('<div class="steel-header"><span class="steel-text steel-subheader">Risk Governance & Compliance</span></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f'<div class="big-badge" style="background: linear-gradient(135deg, {color}cc, {color}); border: 1px solid {color}; box-shadow: 0 0 20px {color}66;">GOVERNANCE STATUS: {status}</div>', unsafe_allow_html=True)
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
        
        m1, m2, m3 = st.columns(3)
        
        credit_val = latest_monitor['Credit_Delta']
        credit_status = "STRESS" if credit_val < -0.015 else "NOMINAL"
        m1.metric("Credit Spreads", f"{credit_val:.2%}", 
                 delta="STABLE" if credit_status=="NOMINAL" else "WIDENING", 
                 delta_color="normal" if credit_status=="NOMINAL" else "inverse",
                 help="Tracks High Yield bonds vs Treasuries.")

        dxy_val = latest_monitor['DXY_Delta']
        dxy_status = "SPIKE" if dxy_val > 0.02 else "STABLE"
        m2.metric("US Dollar", f"{dxy_val:.2%}", 
                 delta="STABLE" if dxy_status=="STABLE" else "SPIKING", 
                 delta_color="inverse",
                 help="Tracks value of USD.")

        breadth_val = latest_monitor['Breadth_Delta']
        breadth_status = "NARROWING" if breadth_val < -0.025 else "HEALTHY"
        m3.metric("Market Breadth", f"{breadth_val:.2%}", 
                 delta=breadth_status, 
                 delta_color="normal" if breadth_status=="HEALTHY" else "inverse",
                 help="Compares Equal Weight S&P to Cap Weight.")

    # ---------------------------
    # TAB 3: STRATEGIST VIEW
    # ---------------------------
    with tab3:
        st.markdown('<div class="steel-header"><span class="steel-text steel-subheader">MacroEffects: Chief Strategist\'s View</span></div>', unsafe_allow_html=True)
        
        try:
            SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4ik-SBHr_ER_SyMHgwVAds3UaxRtPTA426qU_26TuHkHlyb5h6zl8_H9E-_Kw5FUO3W1mBU8CKiZP/pub?gid=0&single=true&output=csv" 
            
            if "INSERT_YOUR" in SHEET_URL:
                update_df = pd.read_csv("data/update.csv")
            else:
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

else:
    st.error("Data connection offline. Please check network.")

# FOOTER
st.markdown("""
<div class="custom-footer">
MACROEFFECTS | ALPHA SWARM PROTOCOL v18.0 | INSTITUTIONAL RISK GOVERNANCE<br>
Disclaimer: This tool provides market analysis for informational purposes only. Not financial advice.<br>
<br>
<strong>Institutional Access:</strong> <a href="mailto:institutional@macroeffects.com" style="color: inherit; text-decoration: none; font-weight: bold;">institutional@macroeffects.com</a>
</div>
""", unsafe_allow_html=True)