import streamlit as st
import os
import base64
import plotly.graph_objects as go

def apply_theme():
    """Initializes session state, injects CSS, and returns theme constants."""
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False

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

    return {
        "BG_COLOR": BG_COLOR,
        "ACCENT_GOLD": ACCENT_GOLD,
        "CHART_TEMPLATE": CHART_TEMPLATE,
        "CHART_FONT": CHART_FONT
    }

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

def render_market_card(name, price, delta, pct):
    delta_color = "#00d26a" if delta >= 0 else "#f93e3e"
    return f"""
<div class="market-card" role="group" aria-label="{name} Market Data">
<div class="market-ticker">{name}</div>
<div class="market-price">{price:,.2f}</div>
<div class="market-delta" style="color: {delta_color};">{delta:+.2f} ({pct:+.2f}%)</div>
</div>
""".strip()

def render_sparkline(data, line_color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', line=dict(color=line_color, width=2), hoverinfo='skip'))
    fig.update_layout(
        height=40, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_header_html(img_b64):
    img_tag = f'<img src="data:image/png;base64,{img_b64}" alt="MacroEffects Shield Logo" style="height: 50px; width: auto; flex-shrink: 0; object-fit: contain;">' if img_b64 else ''
    return f"""
<div class="header-bar">
{img_tag}
<div class="header-text-col">
<span class="steel-text-main">MacroEffects</span>
<span class="steel-text-sub">AI Inference & Risk Intelligence</span>
</div>
</div>
""".strip()

FOOTER_HTML = """
<div class="custom-footer">
MACROEFFECTS | ALPHA SWARM PROTOCOL v55.1 | INSTITUTIONAL RISK GOVERNANCE<br>
Disclaimer: This tool provides market analysis for informational purposes only. Not financial advice.<br>
<br>
<strong>Institutional Access:</strong> <a href="mailto:institutional@macroeffects.com" style="color: inherit; text-decoration: none; font-weight: bold;">institutional@macroeffects.com</a>
</div>
"""
