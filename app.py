import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import styles
import logic

# 1. SETUP & THEME
theme = styles.apply_theme()

# 2. EXECUTION PHASE
try:
    with st.spinner("Connecting to Global Swarm..."):
        full_data = logic.fetch_market_data()
        strat_data = logic.load_strategist_data()
    if full_data is not None and not full_data.empty:
        closes = full_data['Close']
        gov_df, status, color, reason = logic.calc_governance(full_data)
        latest_monitor = gov_df.iloc[-1]
    else:
        status, color, reason, closes, latest_monitor = "DATA ERROR", "#ff0000", "Data Feed Unavailable", None, None
except Exception:
    status, color, reason, full_data, closes, latest_monitor = "SYSTEM ERROR", "#ff0000", "Connection Failed", None, None, None

# 3. UI LAYOUT
c_title, c_menu = st.columns([0.90, 0.10], gap="small")
with c_title:
    st.markdown(styles.create_header_html(styles.get_base64_image("shield.png")), unsafe_allow_html=True)

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
    with tab1:
        st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">Global Asset Grid</span></div>', unsafe_allow_html=True)
        assets = [{"name": "Dow Jones", "ticker": "^DJI", "color": "#00CC00"}, {"name": "S&P 500", "ticker": "SPY", "color": "#00CC00"},
                  {"name": "Nasdaq", "ticker": "^IXIC", "color": "#00CC00"}, {"name": "VIX Index", "ticker": "^VIX", "color": "#FF5500"},
                  {"name": "Gold", "ticker": "GC=F", "color": "#FFD700"}, {"name": "Crude Oil", "ticker": "CL=F", "color": "#888888"}]
        
        def render_row(asset_slice):
            for i, col in enumerate(st.columns(3)):
                if i < len(asset_slice):
                    asset = asset_slice[i]
                    with col:
                        if asset['ticker'] in closes:
                            s = closes[asset['ticker']].dropna()
                            if not s.empty:
                                cur, prev = s.iloc[-1], s.iloc[-2]
                                st.markdown(styles.render_market_card(asset['name'], cur, cur-prev, ((cur-prev)/prev)*100), unsafe_allow_html=True)
                                st.plotly_chart(styles.render_sparkline(s.tail(30), asset['color']), use_container_width=True, config={'displayModeBar': False})
        render_row(assets[:3]); st.markdown("---"); render_row(assets[3:])
        
        st.divider(); st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">Swarm Deep Dive</span></div>', unsafe_allow_html=True)
        if 'SPY' in closes:
            spy = closes['SPY']
            ppo, sig, hist = logic.calc_ppo(spy)
            sma, std, u_cone, l_cone = logic.calc_cone(spy)
            f_dates, f_mean, f_upper, f_lower = logic.generate_forecast(spy.index[-1], spy.iloc[-1], std.iloc[-1], days=30)
            
            c1, c2 = st.columns(2)
            with c1: view_mode = st.radio("Select View Horizon:", ["Tactical (60-Day Zoom)", "Strategic (2-Year History)"], horizontal=True)
            with c2: st.radio("Market Scope (Premium):", ["US Market (Active)", "Global Swarm 🔒", "Sector Rotation 🔒"], index=0, horizontal=True, disabled=True, help="Institutional-grade data feeds (Global/Sector) are locked.")

            start_filter = (datetime.now() - timedelta(days=60 if "Tactical" in view_mode else 730)).strftime('%Y-%m-%d')
            c_data = full_data[full_data.index >= start_filter]
            c_lower, c_upper = l_cone[l_cone.index >= start_filter], u_cone[u_cone.index >= start_filter]

            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
            fig.add_trace(go.Scatter(x=c_data.index, y=c_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
            fig.add_trace(go.Scatter(x=c_data.index, y=c_upper, fill='tonexty', fillcolor='rgba(0, 100, 255, 0.1)', line=dict(width=0), name="Fair Value Cone", hoverinfo='skip'), row=1, col=1)
            fig.add_trace(go.Candlestick(x=c_data.index, open=c_data['Open']['SPY'], high=c_data['High']['SPY'], low=c_data['Low']['SPY'], close=c_data['Close']['SPY'], name='SPY'), row=1, col=1)

            if "Tactical" in view_mode and strat_data is not None:
                latest = strat_data.iloc[-1]
                dates_fut = [latest['Date'] + timedelta(days=30*i) for i in range(1, 7)]
                prices_fut = [latest['Tstk_Adj'] * (1 + latest[f'FP{i}']) for i in range(1, 7)]
                fig.add_trace(go.Scatter(x=dates_fut, y=prices_fut, name="Strategist Forecast", line=dict(color=theme["ACCENT_GOLD"], width=3, dash='dot'), mode='lines+markers'), row=1, col=1)
            elif "Tactical" in view_mode:
                fig.add_trace(go.Scatter(x=f_dates, y=f_lower, line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
                fig.add_trace(go.Scatter(x=f_dates, y=f_upper, fill='tonexty', fillcolor='rgba(200, 0, 255, 0.15)', line=dict(width=0), name="Proj. Uncertainty", hoverinfo='skip'), row=1, col=1)
                fig.add_trace(go.Scatter(x=f_dates, y=f_mean, name="Swarm Forecast", line=dict(color=theme["CHART_FONT"], width=2, dash='dot')), row=1, col=1)

            sub_ppo = ppo[ppo.index >= c_data.index[0]]
            fig.add_trace(go.Scatter(x=c_data.index, y=sub_ppo, name="Swarm Trend", line=dict(color='cyan', width=1)), row=2, col=1)
            fig.add_trace(go.Scatter(x=c_data.index, y=sig[sig.index >= c_data.index[0]], name="Signal", line=dict(color='orange', width=1)), row=2, col=1)
            fig.add_trace(go.Bar(x=c_data.index, y=hist[hist.index >= c_data.index[0]], name="Velocity", marker_color=['#00ff00' if v >= 0 else '#ff0000' for v in hist[hist.index >= c_data.index[0]]]), row=2, col=1)

            fig.update_layout(height=500, template=theme["CHART_TEMPLATE"], margin=dict(l=0, r=0, t=0, b=0), showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color=theme["CHART_FONT"]), xaxis_rangeslider_visible=False)
            fig.update_xaxes(showgrid=False); fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("""<div class="premium-banner">🔒 Institutional Access Required: Unlock Sector Rotation & Global Flows</div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">Risk Governance & Compliance</span></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        c1.markdown(f'<div class="gov-pill" style="background: linear-gradient(135deg, {color}, {color}88); border: 1px solid {color};">{status}</div>', unsafe_allow_html=True)
        c1.caption(f"Reason: {reason}")
        if '^VIX' in closes: c2.metric("Risk (VIX)", f"{closes['^VIX'].iloc[-1]:.2f}", delta_color="inverse", help="VIX Index")
        st.subheader("⏱️ Tactical Horizons")
        if 'SPY' in closes:
            ppo_vals = logic.calc_ppo(closes['SPY'])
            c = st.columns(3)
            c[0].info("**1 WEEK**"); c[0].markdown("🟢 **RISING**" if ppo_vals[2].iloc[-1] > 0 else "🔴 **WEAKENING**")
            c[1].info("**1 MONTH**"); c[1].markdown("🟢 **BULLISH**" if ppo_vals[0].iloc[-1] > 0 else "🔴 **BEARISH**")
            c[2].info("**6 MONTH**"); c[2].markdown("🟢 **SAFE**" if status == "NORMAL OPS" else f"🔴 **{status}**")
        st.divider(); st.subheader("📡 Active Monitor Feed (Live Logic)")
        if latest_monitor is not None:
            c = st.columns(3)
            c[0].metric("Credit Spreads", f"{latest_monitor['Credit_Delta']:.2%}", delta="STABLE" if latest_monitor['Credit_Delta'] >= -0.015 else "WIDENING", delta_color="normal" if latest_monitor['Credit_Delta'] >= -0.015 else "inverse")
            c[1].metric("US Dollar", f"{latest_monitor['DXY_Delta']:.2%}", delta="STABLE" if latest_monitor['DXY_Delta'] <= 0.02 else "SPIKING", delta_color="inverse")
            c[2].metric("Market Breadth", f"{latest_monitor['Breadth_Delta']:.2%}", delta="HEALTHY" if latest_monitor['Breadth_Delta'] >= -0.025 else "NARROWING", delta_color="normal" if latest_monitor['Breadth_Delta'] >= -0.025 else "inverse")

    with tab3:
        st.markdown('<div class="steel-sub-header"><span class="steel-text-main" style="font-size: 20px !important;">MacroEffects: Chief Strategist\'s View</span></div>', unsafe_allow_html=True)
        try:
            update_df = logic.get_strategist_update()
            if update_df is not None:
                update_data = dict(zip(update_df['Key'], update_df['Value']))
                with st.expander(f"Read Forecast ({update_data.get('Date', 'Current')})", expanded=True):
                    st.markdown(f'**"{update_data.get("Title", "Market Update")}"**')
                    st.markdown(str(update_data.get('Text', '')).replace("\\n", "\n"))
                st.info("💡 **Analyst Note:** This commentary is pulled live from the Chief Strategist's desk via the Alpha Swarm CMS.")
            else: st.warning("Strategist feed temporarily unavailable.")
        except Exception: st.warning("Strategist feed temporarily unavailable.")
else: st.error("Data connection initializing or offline. Please check network.")
st.markdown(styles.FOOTER_HTML, unsafe_allow_html=True)
