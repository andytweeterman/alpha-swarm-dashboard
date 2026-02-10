import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(page_title="MacroEffects | Global Command", page_icon="M", layout="wide")

# INITIALIZE SESSION STATE
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# SAFE DEFAULTS
full_data = None
closes = None
latest_monitor = None
status = "SYSTEM BOOT"
color = "#888888"

# ==========================================
# 2. THEME ENGINE (HIGH CONTRAST)
# ==========================================
current_theme = {
    "bg_color": "#0e1117" if st.session_state["dark_mode"] else "#ffffff",
    "card_bg": "rgba(22, 27, 34, 0.7)" if st.session_state["dark_mode"] else "rgba(255, 255, 255, 0.9)",
    "card_border": "1px solid rgba(255, 255, 255, 0.08)" if st.session_state["dark_mode"] else "1px solid rgba(49, 51, 63, 0.1)",
    "text_primary": "#F0F2F6" if st.session_state["dark_mode"] else "#31333F", # Bright White for Dark Mode
    "text_secondary": "#B0B8C1" if st.session_state["dark_mode"] else "#555555", # Light Grey for Dark Mode
    "accent_gold": "#C6A87C",
    "chart_template": "plotly_dark" if st.session_state["dark_mode"] else "plotly_white",
    "chart_font": "#E6E6E6" if st.session_state["dark_mode"] else "#31333F"
}

# ==========================================
# 3. CSS STYLING (TEXT ENFORCER)
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Fira+Code:wght@300;500;700&display=swap');

:root {{
    --bg-color: {current_theme['bg_color']};
    --card-bg: {current_theme['card_bg']};
    --card-border: {current_theme['card_border']};
    --text-primary: {current_theme['text_primary']};
    --text-secondary: {current_theme['text_secondary']};
    --accent-gold: {current_theme['accent_gold']};
}}

.stApp {{ background-color: var(--bg-color) !important; font-family: 'Inter', sans-serif; }}

/* --- TEXT READABILITY ENFORCERS --- */

/* 1. Force Paragraphs and Spans to use Primary Color */
.stMarkdown p, .stMarkdown span, .stMarkdown li {{
    color: var(--text-primary) !important;
}}

/* 2. Force Radio Button Labels */
div[role="radiogroup"] label p {{
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}}

/* 3. Force Metrics (Value and Label) */
div[data-testid="stMetricValue"] {{
    color: var(--text-primary) !important;
}}
div[data-testid="stMetricLabel"] {{
    color: var(--text-secondary) !important;
}}

/* 4. Force Expander Text */
.streamlit-expanderContent p {{
    color: var(--text-primary) !important;
}}

/* 5. Force Headers */
h1, h2, h3, h4, h5, h6 {{
    color: var(--text-primary) !important;
}}

/* REMOVE DEFAULT UI */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}} 

/* LAYOUT TWEAKS */
.block-container {{ padding-top: 1rem !important; padding-bottom: 2rem !important; }}
div[data-testid="column"] {{ padding: 0px !important; }}
div[data-testid="stHorizontalBlock"] {{ gap: 0rem !important; }}

/* HEADER CONTAINER */
.steel-header-container {{
    background: linear-gradient(145deg, #1a1f26, #2d343f);
    padding: 0px 20px;
    border-radius: 8px 0 0 8px; 
    border: 1px solid #4a4f58;
    border-right: none; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    margin-bottom: 5px; 
    height: 80px; 
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.steel-text {{
    background: linear-gradient(180deg, #FFFFFF 0%, #A0A0A0 50%, #E0E0E0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 0;
    line-height: 1.1;
    font-size: 26px !important;
}}

.tagline-text {{
    color: #F0F0F0 !important; 
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
    line-height: 1.1;
    opacity: 0.8;
}}

/* MENU BUTTON INTEGRATION */
[data-testid="stPopover"] button {{
    border: 1px solid #4a4f58;
    background: linear-gradient(145deg, #1a1f26, #2d343f);
    color: #C6A87C; 
    font-size: 28px !important;
    font-weight: bold;
    height: 80px; 
    width: 100%;
    margin-top: 0px;
    border-radius: 0 8px 8px 0; 
    border-left: 1px solid #4a4f58;
    display: flex;
    align-items: center;
    justify-content: center;
}}
[data-testid="stPopover"] button:hover {{ border-color: #C6A87C; color: #FFFFFF; }}

/* TABS */
button[data-baseweb="tab"] {{
    background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.05) 100%) !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
    border-radius: 6px 6px 0 0 !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 14px;
    text-transform: uppercase;
    padding: 10px 10px;
    margin-right: 2px;
    flex-grow: 1;
}}

@media (max-width: 640px) {{
    button[data-baseweb="tab"] {{
        font-size: 11px !important;
        padding: 8px 4px !important;
    }}
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    background: linear-gradient(180deg, #2d343f 0%, #1a1f26 100%) !important;
    border-top: 2px solid var(--accent-gold) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] p {{
    color: #FFFFFF !important;
}}

/* COMPONENT STYLES */
.steel-sub-header {{
    background: linear-gradient(145deg, #1a1f26, #2d343f);
    padding: 8px 15px;
    border-radius: 6px;
    border: 1px solid #4a4f58;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    margin-bottom: 15px;
}}

.mini-badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-family: 'Fira Code', monospace; font-size: 11px; font-weight: bold; color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.2); margin-left: 10px; vertical-align: middle; }}
.premium-pill {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 800; color: #3b2c00; background: linear-gradient(135deg, #bf953f 0%, #fcf6ba 100%); box-shadow: 0 2px 5px rgba(0,0,0,0.2); margin-left: 5px; vertical-align: middle; letter-spacing: 1px; }}

.market-card {{ background: var(--card-bg); border: var(--card-border); border-radius: 6px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; margin-bottom: 10px; }}
.market-ticker {{ color: var(--text-secondary); font-size: 11px; margin-bottom: 2px; }}
.market-price {{ color: {current_theme['text_primary']}; font-family: 'Fira Code', monospace; font-size: 22px; font-weight: 700; margin: 2px 0; }}
.market-delta {{ font-family: 'Fira Code', monospace; font-size: 13px; font-weight: 600; }}

[data-testid="stExpander"] {{ background-color: rgba(255,255,255,0.02) !important; border: 1px solid #30363d !important; border-radius: 4px; }}
[data-testid="stExpander"] summary {{ color: var(--text-primary) !important; font-family: 'Fira Code', monospace; font-size: 13px; }}

/* FOOTER FIX */
.custom-footer {{
    font-family: 'Fira Code', monospace;
    font-size: 10px;
    color: var(--text-secondary) !important; /* DYNAMIC COLOR FIX */
    text-align: center;
    margin-top: 50px;
    border-top: 1px solid #30363d;
    padding-top: 20px;
    text-transform: uppercase;
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
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

def render_sparkline(data, line_color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', line=dict(color=line_color, width=2), hoverinfo='skip'))
    fig.update_layout(
        height=40, margin=dict(l=0,r=0,t=0,b=0), 
        xaxis=dict(visible=False), yaxis=dict(visible=False), 
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# ==========================================
# 5. EXECUTION PHASE
# ==========================================
try:
    with st.spinner("Connecting to Global Swarm..."):
        full_data = fetch_market_data()
        
    if full_data is not None and not full_data.empty:
        closes = full_data['Close']
        gov_df, status, color, reason = calc_governance(full_data)
        latest_monitor = gov_df.iloc[-1]
    else:
        status, color, reason = "DATA ERROR", "#ff0000", "Data Feed Unavailable"
except Exception as e:
    status, color, reason = "SYSTEM ERROR", "#ff0000", "Connection Failed"

# ==========================================
# 6. UI LAYOUT
# ==========================================

# HEADER (85/15 Ratio)
c_title, c_menu = st.columns([0.85, 0.15])

with c_title:
    st.markdown(f"""
    <div class="steel-header-container">
        <span class="steel-text">MacroEffects</span>
        <span class="tagline-text">AI INFERENCE FOCUSED ON STOCK MARKETS</span>
    </div>
    """, unsafe_allow_html=True)

with c_menu:
    with st.popover("☰", use_container_width=True):
        st.caption("Settings & Links")
        is_dark = st.toggle("Dark Mode", value=st.session_state["dark_mode"])
        if is_dark != st.session_state["dark_mode"]:
            st.session_state["dark_mode"] = is_dark
            st.rerun()
        st.divider()
        st.page_link("https://sixmonthstockmarketforecast.com/home/", label="Six Month Forecast", icon="📈")
        st.link_button("User Guide", "https://github.com/andytweeterman/alpha-swarm-dashboard/blob/main/docs/USER_GUIDE.md") 
        st.link_button("About Us", "https://sixmonthstockmarketforecast.com/about") 
        st.link_button("Contact Analyst", "mailto:analyst@macroeffects.com")

# SUBHEADER
st.markdown(f"""
<div style="margin-bottom: 20px; margin-top: 15px;">
    <span style="font-family: 'Inter'; font-weight: 600; font-size: 16px; color: var(--text-secondary);">Macro-Economic Intelligence: Global Market Command Center</span>
    <div class="mini-badge" style="background-color: {color};">{status}</div>
    <div class="premium-pill">PREMIUM</div>
</div>
""", unsafe_allow_html=True)

st.divider()

if full_data is not None and closes is not None:
    
    tab1, tab2, tab3 = st.tabs(["Markets", "Risk", "Strategist"])

    # --- TAB 1: MARKETS ---
    with tab1:
        st.markdown('<div class="steel-sub-header"><span class="steel-text" style="font-size: 20px !important;">Global Asset Grid</span></div>', unsafe_allow_html=True)
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
                if asset['ticker'] in closes:
                    series = closes[asset['ticker']].dropna()
                    if not series.empty:
                        current = series.iloc[-1]; prev = series.iloc[-2]; delta = current - prev; pct = (delta / prev) * 100
                        delta_color = "#00d26a" if delta >= 0 else "#f93e3e"
                        st.markdown(f"""<div class="market-card"><div class="market-ticker">{asset['name']}</div><div class="market-price">{current:,.2f}</div><div class="market-delta" style="color: {delta_color};">{delta:+.2f} ({pct:+.2f}%)</div></div>""", unsafe_allow_html=True)
                        st.plotly_chart(render_sparkline(series.tail(30), asset['color']), use_container_width=True, config={'displayModeBar': False})
        st.markdown("---")
        c4, c5, c6 = st.columns(3)
        for i, col in enumerate([c4, c5, c6]):
            asset = assets[i+3]
            with col:
                if asset['ticker'] in closes:
                    series = closes[asset['ticker']].dropna()
                    if not series.empty:
                        current = series.iloc[-1]; prev = series.iloc[-2]; delta = current - prev; pct = (delta / prev) * 100
                        delta_color = "#00d26a" if delta >= 0 else "#f93e3e"
                        st.markdown(f"""<div class="market-card"><div class="market-ticker">{asset['name']}</div><div class="market-price">{current:,.2f}</div><div class="market-delta" style="color: {delta_color};">{delta:+.2f} ({pct:+.2f}%)</div></div>""", unsafe_allow_html=True)
                        st.plotly_chart(render_sparkline(series.tail(30), asset['color']), use_container_width=True, config={'displayModeBar': False})
        
        st.divider()
        
        # DEEP DIVE
        st.markdown('<div class="steel-sub-header"><span class="steel-text" style="font-size: 20px !important;">Swarm Deep Dive</span></div>', unsafe_allow_html=True)
        if 'SPY' in closes:
            spy_close = closes['SPY']
            ppo, sig, hist = calc_ppo(spy_close)
            sma, std, upper_cone, lower_cone = calc_cone(spy_close)
            last_date = spy_close.index[-1]; last_val = spy_close.iloc[-1]; last_dev = std.iloc[-1]
            f_dates, f_mean, f_upper, f_lower = generate_forecast(last_date, last_val, last_dev, days=30)
            
            c1, c2 = st.columns(2)
            with c1: view_mode = st.radio("Select View Horizon:", ["Tactical (60-Day Zoom)", "Strategic (2-Year History)"], horizontal=True)
            with c2: st.radio("Market Scope (Premium):", ["US Market (Active)", "Global Swarm 🔒", "Sector Rotation 🔒"], index=0, horizontal=True, disabled=True)

            if view_mode == "Tactical (60-Day Zoom)": start_filter = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'); show_forecast = True
            else: start_filter = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d'); show_forecast = False
            
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
                fig.add_trace(go.Scatter(x=f_dates, y=f_mean, name="Swarm Forecast", line=dict(color=current_theme['chart_font'], width=2, dash='dot')), row=1, col=1)

            subset_ppo = ppo[ppo.index >= chart_data.index[0]]; subset_sig = sig[sig.index >= chart_data.index[0]]; subset_hist = hist[hist.index >= chart_data.index[0]]
            fig.add_trace(go.Scatter(x=chart_data.index, y=subset_ppo, name="Swarm Trend", line=dict(color='cyan', width=1)), row=2, col=1)
            fig.add_trace(go.Scatter(x=chart_data.index, y=subset_sig, name="Signal", line=dict(color='orange', width=1)), row=2, col=1)
            colors = ['#00ff00' if val >= 0 else '#ff0000' for val in subset_hist]
            fig.add_trace(go.Bar(x=chart_data.index, y=subset_hist, name="Velocity", marker_color=colors), row=2, col=1)

            fig.update_layout(
                height=500, 
                template=current_theme['chart_template'], 
                margin=dict(l=0, r=0, t=0, b=0), 
                showlegend=False, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color=current_theme['chart_font']), 
                xaxis_rangeslider_visible=False
            )
            fig.update_xaxes(showgrid=False); fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        st.markdown("""<div class="premium-banner">🔒 Institutional Access Required: Unlock Sector Rotation & Global Flows</div>""", unsafe_allow_html=True)

    # --- TAB 2: RISK ---
    with tab2:
        st.markdown('<div class="steel-sub-header"><span class="steel-text" style="font-size: 20px !important;">Risk Governance & Compliance</span></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f'<div class="big-badge" style="background: linear-gradient(135deg, {color}cc, {color}); border: 1px solid {color}; box-shadow: 0 0 20px {color}66;">GOVERNANCE STATUS: {status}</div>', unsafe_allow_html=True)
            st.caption(f"Reason: {reason}")
        with col2:
            if '^VIX' in closes:
                latest_vix = closes['^VIX'].iloc[-1]
                st.metric("Risk (VIX)", f"{latest_vix:.2f}", delta_color="inverse")

        st.subheader("⏱️ Tactical Horizons")
        if 'SPY' in closes:
            latest_hist = calc_ppo(closes['SPY'])[2].iloc[-1]
            latest_ppo = calc_ppo(closes['SPY'])[0].iloc[-1]
            h1, h2, h3 = st.columns(3)
            with h1: st.info("**1 WEEK (Momentum)**"); st.markdown("🟢 **RISING**" if latest_hist > 0 else "🔴 **WEAKENING**")
            with h2: st.info("**1 MONTH (Trend)**"); st.markdown("🟢 **BULLISH**" if latest_ppo > 0 else "🔴 **BEARISH**")
            with h3: st.info("**6 MONTH (Structural)**"); st.markdown("🟢 **SAFE**" if status == "NORMAL OPS" else f"🔴 **{status}**")

        st.divider()
        st.subheader("📡 Active Monitor Feed (Live Logic)")
        if latest_monitor is not None:
            m1, m2, m3 = st.columns(3)
            credit_val = latest_monitor['Credit_Delta']
            credit_status = "STRESS" if credit_val < -0.015 else "NOMINAL"
            m1.metric("Credit Spreads", f"{credit_val:.2%}", delta="STABLE" if credit_status=="NOMINAL" else "WIDENING", delta_color="normal" if credit_status=="NOMINAL" else "inverse", help="Tracks High Yield bonds vs Treasuries.")

            dxy_val = latest_monitor['DXY_Delta']
            dxy_status = "SPIKE" if dxy_val > 0.02 else "STABLE"
            m2.metric("US Dollar", f"{dxy_val:.2%}", delta="STABLE" if dxy_status=="STABLE" else "SPIKING", delta_color="inverse", help="Tracks value of USD.")

            breadth_val = latest_monitor['Breadth_Delta']
            breadth_status = "NARROWING" if breadth_val < -0.025 else "HEALTHY"
            m3.metric("Market Breadth", f"{breadth_val:.2%}", delta=breadth_status, delta_color="normal" if breadth_status=="HEALTHY" else "inverse", help="Compares Equal Weight S&P to Cap Weight.")

    # --- TAB 3: STRATEGIST ---
    with tab3:
        st.markdown('<div class="steel-sub-header"><span class="steel-text" style="font-size: 20px !important;">MacroEffects: Chief Strategist\'s View</span></div>', unsafe_allow_html=True)
        
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

            with st.expander(f"Read Forecast ({up_date})", expanded=True):
                st.markdown(f'**"{up_title}"**')
                st.markdown(up_text)
            st.info("💡 **Analyst Note:** This commentary is pulled live from the Chief Strategist's desk via the Alpha Swarm CMS.")
        except Exception:
            st.warning("Strategist feed temporarily unavailable.")

else:
    st.error("Data connection initializing or offline. Please check network.")

# FOOTER
st.markdown("""
<div class="custom-footer">
MACROEFFECTS | ALPHA SWARM PROTOCOL v30.0 | INSTITUTIONAL RISK GOVERNANCE<br>
Disclaimer: This tool provides market analysis for informational purposes only. Not financial advice.<br>
<br>
<strong>Institutional Access:</strong> <a href="mailto:institutional@macroeffects.com" style="color: inherit; text-decoration: none; font-weight: bold;">institutional@macroeffects.com</a>
</div>
""", unsafe_allow_html=True)