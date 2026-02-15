import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import base64

# ==========================================
# HELPER FUNCTIONS
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

# ==========================================
# 2. THEME ENGINE
# ==========================================
if st.session_state["dark_mode"]:
    # DARK MODE
    BG_COLOR = "#0e1117"
    CARD_BG = "rgba(22, 27, 34, 0.7)"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#E0E0E0"
    CHART_TEMPLATE = "plotly_dark"
    CHART_FONT = "#E6E6E6"
else:
    # LIGHT MODE
    BG_COLOR = "#ffffff"
    CARD_BG = "rgba(255, 255, 255, 0.9)"
    TEXT_PRIMARY = "#000000"
    TEXT_SECONDARY = "#444444"
    CHART_TEMPLATE = "plotly_white"
    CHART_FONT = "#111111"

ACCENT_GOLD = "#C6A87C"

# ==========================================
# 3. CSS STYLING
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Fira+Code:wght@300;500;700&display=swap');

:root {{
    --bg-color: {BG_COLOR};
    --card-bg: {CARD_BG};
    --text-primary: {TEXT_PRIMARY};
    --text-secondary: {TEXT_SECONDARY};
    --accent-gold: {ACCENT_GOLD};
}}

.stApp {{ background-color: var(--bg-color) !important; font-family: 'Inter', sans-serif; }}

/* --- TEXT ENFORCERS --- */
.stMarkdown p, .stMarkdown span, .stMarkdown li {{ color: var(--text-primary) !important; }}
h3 {{ color: var(--text-secondary) !important; font-weight: 600 !important; }}

/* --- HEADER CONTAINER (Seamless Black) --- */
.header-bar {{
    background: #000000; /* Pure Black */
    height: 70px;
    display: flex;
    flex-direction: row; /* Ensure logo and text are side-by-side */
    align-items: center;
    padding-left: 15px;
    padding-right: 15px;
    border: 1px solid #333333;
    border-right: none;
    border-radius: 8px 0 0 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    overflow: hidden;
}}

/* CONTAINER FOR STACKED TEXT */
.header-text-col {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-left: 12px;
    line-height: 1.1;
}}

/* BRUSHED STEEL TEXT - MAIN TITLE */
.steel-text-main {{
    background: linear-gradient(180deg, #FFFFFF 0%, #E0E0E0 40%, #A0A0A0 55%, #FFFFFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 24px; /* Large for visibility */
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* BRUSHED STEEL TEXT - SUBTITLE */
.steel-text-sub {{
    background: linear-gradient(180deg, #E0E0E0 0%, #A0A0A0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 10px; /* Small to fit mobile width */
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
    white-space: nowrap; /* Keep on one line if possible */
}}

/* MOBILE ADJUSTMENT: If screen is VERY small, allow subtitle to wrap */
@media (max-width: 400px) {{
    .steel-text-sub {{
        font-size: 9px;
        white-space: normal;
    }}
}}

/* MENU BUTTON STYLING */
[data-testid="stPopover"] button {{
    border: 1px solid #333333;
    background: #000000;
    color: #C6A87C; 
    font-size: 28px !important;
    font-weight: bold;
    height: 70px; 
    width: 100%;
    margin-top: 0px;
    border-radius: 0 8px 8px 0; 
    border-left: 1px solid #333333;
    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
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
button[data-baseweb="tab"][aria-selected="true"] {{
    background: linear-gradient(180deg, #2d343f 0%, #1a1f26 100%) !important;
    border-top: 2px solid var(--accent-gold) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] p {{ color: #FFFFFF !important; }}

/* COMPONENTS */
.gov-pill {{
    display: inline-block; padding: 4px 12px; border-radius: 12px;
    font-family: 'Fira Code', monospace; font-size: 11px; font-weight: bold;
    color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.2); margin-left: 10px;
    vertical-align: middle; text-transform: uppercase;
}}
.premium-pill {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 800; color: #3b2c00; background: linear-gradient(135deg, #bf953f 0%, #fcf6ba 100%); box-shadow: 0 2px 5px rgba(0,0,0,0.2); margin-left: 5px; vertical-align: middle; letter-spacing: 1px; }}
.steel-sub-header {{ background: linear-gradient(145deg, #1a1f26, #2d343f); padding: 8px 15px; border-radius: 6px; border: 1px solid #4a4f58; box-shadow: 0 2px 4px rgba(0,0,0,0.3); margin-bottom: 15px; }}
.market-card {{ background: var(--card-bg); border: 1px solid rgba(128,128,128,0.2); border-radius: 6px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; margin-bottom: 10px; }}
.market-ticker {{ color: var(--text-secondary); font-size: 11px; margin-bottom: 2px; }}
.market-price {{ color: var(--text-primary); font-family: 'Fira Code', monospace; font-size: 22px; font-weight: 700; margin: 2px 0; }}
.market-delta {{ font-family: 'Fira Code', monospace; font-size: 13px; font-weight: 600; }}

/* UTILS */
div[data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; font-size: 14px !important; font-weight: 500 !important; }}
div[data-testid="stMetricValue"] {{ color: var(--text-primary) !important; }}
header[data-testid="stHeader"] {{ visibility: hidden; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 1rem !important; padding-bottom: 2rem !important; }}
div[data-testid="column"] {{ padding: 0px !important; }}
div[data-testid="stHorizontalBlock"] {{ gap: 0rem !important; }}

.custom-footer {{
    font-family: 'Fira Code', monospace; font-size: 10px; color: var(--text-secondary) !important;
    text-align: center; margin-top: 50px; border-top: 1px solid #30363d; padding-top: 20px; text-transform: uppercase;
}}
</style>
""", unsafe_allow_html=True)

    # ==========================================
    # 5. EXECUTION PHASE
    # ==========================================
    try:
        tickers = ["SPY", "^DJI", "^IXIC", "HYG", "IEF", "^VIX", "RSP", "DX-Y.NYB", "GC=F", "CL=F"]
        start = (datetime.now() - timedelta(days=1825)).strftime('%Y-%m-%d')
        data = yf.download(tickers, start=start, progress=False)
        return data
    except Exception:
        return None

def get_base64_image(image_path):
    try:
        # Prevent path traversal: limit access to app directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.abspath(os.path.join(base_dir, image_path))

        # Check if the resolved path starts with the base directory
        if os.path.commonpath([base_dir, filepath]) != base_dir:
            return None

        # Ensure it's a valid file
        if not os.path.isfile(filepath):
            return None

        with open(filepath, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
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
    """Ingests the Strategist's Forecast CSV (^GSPC.csv)"""
    try:
        # Look for the file in the current directory
        # You can rename your uploaded file to '^GSPC.csv' to make this work automatically
        possible_files = [f for f in os.listdir() if "GSPC" in f and f.endswith(".csv")]
        if not possible_files:
            return None
        
        filename = possible_files[0] # Pick the first match
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
        strat_data = load_strategist_data()
        
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

# HEADER (90/10 Ratio for tighter fit)
c_title, c_menu = st.columns([0.90, 0.10], gap="small")

with c_title:
    img_b64 = get_base64_image("shield.png")
    
    # NOTE: We construct the HTML string first and use .strip() to ensure no indentation errors.
    if img_b64:
        header_html = f"""
<div class="header-bar">
<img src="data:image/png;base64,{img_b64}" style="height: 50px; width: auto; flex-shrink: 0; object-fit: contain;">
<div class="header-text-col">
<span class="steel-text-main">MacroEffects</span>
<span class="steel-text-sub">AI Inference & Risk Intelligence</span>
</div>
</div>
""".strip()
    else:
        header_html = f"""
<div class="header-bar">
<div class="header-text-col">
<span class="steel-text-main">MacroEffects</span>
<span class="steel-text-sub">AI Inference & Risk Intelligence</span>
</div>
</div>
""".strip()
    
    st.markdown(header_html, unsafe_allow_html=True)

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

# SUBHEADER WITH SMALL PILL
st.markdown(f"""
<div style="margin-bottom: 20px; margin-top: 5px;">
    <span style="font-family: 'Inter'; font-weight: 600; font-size: 16px; color: var(--text-secondary);">Macro-Economic Intelligence: Global Market Command Center</span>
    <div class="gov-pill" style="background: linear-gradient(135deg, {color}, {color}88); border: 1px solid {color};">{status}</div>
    <div class="premium-pill">PREMIUM</div>
</div>
""", unsafe_allow_html=True)

st.divider()

if full_data is not None and closes is not None:
    
    tab1, tab2, tab3 = st.tabs(["Markets", "Risk", "Strategist"])

    # --- TAB 1: MARKETS ---
    with tab1:
        st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">Global Asset Grid</span></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">Swarm Deep Dive</span></div>', unsafe_allow_html=True)
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

            # --- STRATEGIST FORECAST INJECTION (ADDED BACK from v47) ---
            if strat_data is not None and show_forecast:
                # Use the last row of the strategist file
                latest = strat_data.iloc[-1]
                last_price = latest['Tstk_Adj']
                
                # Create future dates (1m, 2m, 3m, etc.)
                base_date = latest['Date']
                dates_fut = [base_date + timedelta(days=30*i) for i in range(1, 7)]
                
                # Calculate Price Targets: Last_Price * (1 + Forecast_Percent)
                prices_fut = [last_price * (1 + latest[f'FP{i}']) for i in range(1, 7)]
                
                # Plot the "Mean Forecast" line (Using FP3 trend as baseline)
                fig.add_trace(go.Scatter(x=dates_fut, y=prices_fut, name="Strategist Forecast", 
                                         line=dict(color=ACCENT_GOLD, width=3, dash='dot'),
                                         mode='lines+markers'), row=1, col=1)
            # --- FALLBACK TO SYNTHETIC CONE IF NO CSV ---
            elif show_forecast:
                fig.add_trace(go.Scatter(x=f_dates, y=f_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
                fig.add_trace(go.Scatter(x=f_dates, y=f_upper, fill='tonexty', fillcolor='rgba(200, 0, 255, 0.15)', line=dict(width=0), name="Proj. Uncertainty", hoverinfo='skip'), row=1, col=1)
                fig.add_trace(go.Scatter(x=f_dates, y=f_mean, name="Swarm Forecast", line=dict(color=CHART_FONT, width=2, dash='dot')), row=1, col=1)
            # -------------------------------------

            subset_ppo = ppo[ppo.index >= chart_data.index[0]]; subset_sig = sig[sig.index >= chart_data.index[0]]; subset_hist = hist[hist.index >= chart_data.index[0]]
            fig.add_trace(go.Scatter(x=chart_data.index, y=subset_ppo, name="Swarm Trend", line=dict(color='cyan', width=1)), row=2, col=1)
            fig.add_trace(go.Scatter(x=chart_data.index, y=subset_sig, name="Signal", line=dict(color='orange', width=1)), row=2, col=1)
            colors = ['#00ff00' if val >= 0 else '#ff0000' for val in subset_hist]
            fig.add_trace(go.Bar(x=chart_data.index, y=subset_hist, name="Velocity", marker_color=colors), row=2, col=1)

            fig.update_layout(
                height=500, 
                template=CHART_TEMPLATE, 
                margin=dict(l=0, r=0, t=0, b=0), 
                showlegend=False, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color=CHART_FONT), 
                xaxis_rangeslider_visible=False
            )
            fig.update_xaxes(showgrid=False); fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        st.markdown("""<div class="premium-banner">🔒 Institutional Access Required: Unlock Sector Rotation & Global Flows</div>""", unsafe_allow_html=True)

    # --- TAB 2: RISK ---
    with tab2:
        st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">Risk Governance & Compliance</span></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f'<div class="gov-pill" style="background: linear-gradient(135deg, {color}, {color}88); border: 1px solid {color};">{status}</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">MacroEffects: Chief Strategist\'s View</span></div>', unsafe_allow_html=True)
        
        try:
            update_df = get_strategist_update()
            if update_df is None:
                raise Exception("No data")

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
MACROEFFECTS | ALPHA SWARM PROTOCOL v55.1 | INSTITUTIONAL RISK GOVERNANCE<br>
Disclaimer: This tool provides market analysis for informational purposes only. Not financial advice.<br>
<br>
<strong>Institutional Access:</strong> <a href="mailto:institutional@macroeffects.com" style="color: inherit; text-decoration: none; font-weight: bold;">institutional@macroeffects.com</a>
</div>
""", unsafe_allow_html=True)
