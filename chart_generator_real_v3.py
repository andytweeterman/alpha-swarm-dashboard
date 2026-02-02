import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import sys

# --- SAFETY BLOCK ---
try:
    print("--- [ALPHA SWARM: REAL DATA + OVERLAY ENGINE] ---")

    # ==========================================
    # 1. LOAD DATA & GOVERNANCE
    # ==========================================
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # A. Load Market Data
    file_name = '^GSPC.csv'
    file_path = os.path.join(script_dir, file_name)

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_name}")
        sys.exit()

    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    print(f"[SUCCESS] Loaded Data: {len(df)} rows.")

    # B. Load Governance Status (The Brain)
    gov_file = os.path.join(script_dir, "governance_status.txt")
    judgment_level = 3 # Default to Normal
    
    if os.path.exists(gov_file):
        try:
            with open(gov_file, "r") as f:
                for line in f:
                    if line.startswith("LEVEL:"):
                        judgment_level = int(line.split(":")[1].strip())
                        break
            print(f"[SUCCESS] Governance Level Loaded: {judgment_level}")
        except:
            print("[WARN] Could not parse governance file. Defaulting to Level 3.")
    else:
        print("[WARN] No governance file found. Run avalanche_logic.py first!")

    # ==========================================
    # 2. CALCULATIONS (Weekly Candles + Cone)
    # ==========================================
    # Resample to Weekly
    weekly_history = df['Tstk_Adj'].resample('W').ohlc()
    history = weekly_history.iloc[-52:] 
    
    # Forecast Curve
    last_row = df.iloc[-1]
    current_price = last_row['Tstk_Adj']
    last_date = df.index[-1]
    
    horizons_weeks = [1, 2, 4.3, 8.6, 13, 26]
    fc_cols = ['FP1wk', 'FP2wk', 'FP1', 'FP2', 'FP3', 'FP6']
    fc_log_returns = last_row[fc_cols].values.astype(float)
    forecast_prices = current_price * np.exp(fc_log_returns)
    
    # Real Sigma (Cone Width)
    actual_cols = ['LnTstk_Delta_1wk', 'LnTstk_Delta_2wk', 'LnTstk_Delta_1mo', 
                   'LnTstk_Delta_2mo', 'LnTstk_Delta_3mo', 'LnTstk_Delta_6mo']
    sigmas = []
    for fc, ac in zip(fc_cols, actual_cols):
        residuals = df[ac] - df[fc]
        sigmas.append(residuals.std())
    sigmas = np.array(sigmas)

    z_score = 1.28 # 80% Confidence
    upper_band = current_price * np.exp(fc_log_returns + z_score * sigmas)
    lower_band = current_price * np.exp(fc_log_returns - z_score * sigmas)

    # ==========================================
    # 3. PLOTTING ENGINE
    # ==========================================
    print("Drawing Chart with Overlay...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(16, 9))

    # Candles
    width_days = 3
    for date, row in history.iterrows():
        color = '#00ff00' if row['close'] >= row['open'] else '#ff3333'
        rect = patches.Rectangle((date - pd.Timedelta(days=width_days/2), min(row['open'], row['close'])), 
                                 pd.Timedelta(days=width_days), abs(row['close'] - row['open']), 
                                 facecolor=color, edgecolor=color)
        ax.add_patch(rect)
        ax.plot([date, date], [row['low'], row['high']], color=color, linewidth=1)

    # Cone
    future_dates = [last_date + pd.Timedelta(weeks=w) for w in horizons_weeks]
    plot_dates = [last_date] + future_dates
    plot_mean = [current_price] + forecast_prices.tolist()
    plot_upper = [current_price] + upper_band.tolist()
    plot_lower = [current_price] + lower_band.tolist()

    ax.fill_between(plot_dates, plot_lower, plot_upper, color='cyan', alpha=0.15, label='80% Confidence Interval')
    ax.plot(plot_dates, plot_mean, color='white', linestyle='--', linewidth=2, label='Swarm Mean Forecast')

    # ==========================================
    # 4. THE JUDGMENT OVERLAY BADGE
    # ==========================================
    status_map = {
        1: ("AGGRESSIVE", "#00ff00"), 2: ("AGGRESSIVE", "#00ff00"),
        3: ("NORMAL OPS", "#00ffff"), 4: ("WATCHLIST", "#00ffff"),
        5: ("CAUTION", "#ff9900"), 6: ("CAUTION", "#ff9900"),
        7: ("EMERGENCY", "#ff0000")
    }
    status_text, status_color = status_map.get(judgment_level, ("UNKNOWN", "white"))

    # Badge Box
    box_x, box_y = 0.02, 0.82
    box_w, box_h = 0.22, 0.14
    rect = patches.FancyBboxPatch((box_x, box_y), box_w, box_h, boxstyle="round,pad=0.02", 
                                  fc='#1a1a1a', ec='gray', transform=ax.transAxes, zorder=10)
    ax.add_patch(rect)
    ax.text(box_x + 0.01, box_y + box_h - 0.03, "JUDGMENT OVERLAY", 
            transform=ax.transAxes, color='white', fontsize=10, fontweight='bold', zorder=11)

    # The Gauge (7 Segments)
    seg_w = (box_w - 0.02) / 7
    for i in range(1, 8):
        if i <= 2: c = '#00ff00'
        elif i <= 4: c = '#00ffff'
        elif i <= 6: c = '#ff9900'
        else: c = '#ff0000'
        
        # Dim the lights that aren't active
        alpha = 1.0 if i == judgment_level else 0.2
        
        r = patches.Rectangle((box_x + 0.01 + (i-1)*seg_w, box_y + 0.06), seg_w - 0.005, 0.025, 
                              transform=ax.transAxes, facecolor=c, alpha=alpha, zorder=11)
        ax.add_patch(r)
        ax.text(box_x + 0.01 + (i-1)*seg_w + seg_w/2, box_y + 0.035, str(i), 
                transform=ax.transAxes, color='white', fontsize=8, ha='center', zorder=11)

    ax.text(box_x + 0.01, box_y + 0.01, f"LEVEL {judgment_level}: {status_text}", 
            transform=ax.transAxes, color=status_color, fontsize=11, fontweight='bold', zorder=11)

    # ==========================================
    # 5. FINAL FORMATTING & SAVE
    # ==========================================
    direction = "BULLISH" if fc_log_returns[0] > 0 else "BEARISH"
    title_text = f"ALPHA SWARM: S&P 500 (Weekly)\nOutlook: {direction} ({fc_log_returns[0]:.2%}) | Volatility: {sigmas[0]:.2%}"
    
    ax.set_title(title_text, fontsize=14, color='white', fontweight='bold', pad=20)
    ax.grid(True, color='gray', alpha=0.2)
    ax.legend(loc='upper left', bbox_to_anchor=(0, 0.8)) # Move legend out of way of badge

    # Zoom Logic
    zoom_start = last_date - pd.Timedelta(weeks=15)
    zoom_end = plot_dates[-1] + pd.Timedelta(weeks=2)
    ax.set_xlim(zoom_start, zoom_end)
    
    visible_highs = history[history.index > zoom_start]['high']
    y_max = max(visible_highs.max(), max(plot_upper)) * 1.02
    y_min = min(visible_highs.min(), min(plot_lower)) * 0.98
    ax.set_ylim(y_min, y_max)

    # Save
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    filename = "Alpha_Swarm_REAL_DATA.png"
    save_path = os.path.join(desktop, filename)
    
    plt.savefig(save_path)
    print(f"\n[SUCCESS] Chart generated with OVERLAY.")
    print(f"Saved to Desktop: {save_path}")

except Exception as e:
    print(f"\n[ERROR] {e}")

input("\nPress ENTER to exit...")