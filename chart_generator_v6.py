import sys
import os

try:
    print("--- [STARTING CHART GENERATOR V6: THE CONE CLOSE-UP] ---")
    
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import pandas as pd

    # ==========================================
    # 1. HIGH VOLATILITY DATA
    # ==========================================
    print("Generating data...")
    np.random.seed(42)
    n_history = 60
    n_forecast = 20
    start_price = 5000 # Adjusted to your mention of "hovering around 5000"

    dates = pd.date_range(end=pd.Timestamp.today(), periods=n_history + n_forecast, freq='B')
    
    closes = np.zeros(n_history)
    opens = np.zeros(n_history)
    highs = np.zeros(n_history)
    lows = np.zeros(n_history)
    closes[0] = start_price

    for i in range(1, n_history):
        change = np.random.normal(0, 45) 
        closes[i] = closes[i-1] + change
        opens[i] = closes[i-1] + np.random.normal(0, 15)
        
        noise_high = abs(np.random.normal(0, 25))
        noise_low = abs(np.random.normal(0, 25))
        highs[i] = max(opens[i], closes[i]) + noise_high
        lows[i] = min(opens[i], closes[i]) - noise_low

    n_sims = 100
    simulations = np.zeros((n_forecast, n_sims))
    simulations[0, :] = closes[-1]

    for t in range(1, n_forecast):
        drift = 1.0 
        shock = np.random.normal(0, 40, n_sims) 
        simulations[t, :] = simulations[t-1, :] + shock + drift

    mean_path = np.mean(simulations, axis=1)
    upper_bound = np.percentile(simulations, 90, axis=1)
    lower_bound = np.percentile(simulations, 10, axis=1)

    # ==========================================
    # 2. PLOTTING ENGINE
    # ==========================================
    print("Drawing chart...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(16, 9))

    # Candles
    width = 0.6
    for i in range(len(closes)):
        color = '#00ff00' if closes[i] > opens[i] else '#ff3333'
        rect = patches.Rectangle((i, min(opens[i], closes[i])), width, abs(closes[i] - opens[i]), 
                                 facecolor=color, edgecolor=color)
        ax.add_patch(rect)
        ax.plot([i + width/2, i + width/2], [lows[i], highs[i]], color=color, linewidth=1)

    # Cone
    future_x = np.arange(n_history - 1, n_history + n_forecast - 1)
    ax.fill_between(future_x, lower_bound, upper_bound, color='cyan', alpha=0.15, label='80% Probability Cone')
    for i in range(15): 
        ax.plot(future_x, simulations[:, i], color='cyan', alpha=0.08, linewidth=0.8)
    ax.plot(future_x, mean_path, color='white', linestyle='--', linewidth=2, label='Swarm Mean Projection')

    # --- THE "CONE-CENTRIC" CAMERA ---
    # 1. Decide how many past days to show (The Context Window)
    # Showing only the last 15 days keeps the scale tight on the cone.
    days_context = 15 
    
    view_start_idx = n_history - days_context
    view_end_idx = n_history + n_forecast - 1

    # 2. Calculate Min/Max of ONLY the visible data
    # We slice the arrays to look only at the window we want to see
    visible_highs = highs[view_start_idx:]
    visible_lows = lows[view_start_idx:]
    visible_upper = upper_bound # All forecast is visible
    visible_lower = lower_bound

    # Combine them to find the "Scene Limits"
    scene_max = max(np.max(visible_highs), np.max(visible_upper))
    scene_min = min(np.min(visible_lows), np.min(visible_lower))

    # 3. Apply the Camera Settings
    # X-Axis: Start at history-15, End at end of forecast
    ax.set_xlim(view_start_idx, view_end_idx)
    
    # Y-Axis: Fit exactly to the scene (with tiny padding)
    scene_range = scene_max - scene_min
    padding = scene_range * 0.05 # 5% padding
    ax.set_ylim(scene_min - padding, scene_max + padding)
    # ---------------------------------

    # ==========================================
    # 3. JUDGMENT OVERLAY (LEVEL 3)
    # ==========================================
    judgment_level = 3  
    status_map = {3: ("NORMAL OPS", "#00ffff")}
    status_text, status_color = status_map.get(judgment_level, ("UNKNOWN", "white"))

    box_x, box_y = 0.02, 0.82
    box_w, box_h = 0.22, 0.14
    rect = patches.FancyBboxPatch((box_x, box_y), box_w, box_h, boxstyle="round,pad=0.02", 
                                  fc='#1a1a1a', ec='gray', transform=ax.transAxes, zorder=10)
    ax.add_patch(rect)
    ax.text(box_x + 0.01, box_y + box_h - 0.03, "JUDGMENT OVERLAY", 
            transform=ax.transAxes, color='white', fontsize=10, fontweight='bold', zorder=11)

    seg_w = (box_w - 0.02) / 7
    for i in range(1, 8):
        if i <= 2: c = '#00ff00'
        elif i <= 4: c = '#00ffff'
        elif i <= 6: c = '#ff9900'
        else: c = '#ff0000'
        alpha = 1.0 if i == judgment_level else 0.3
        r = patches.Rectangle((box_x + 0.01 + (i-1)*seg_w, box_y + 0.06), seg_w - 0.005, 0.025, 
                              transform=ax.transAxes, facecolor=c, alpha=alpha, zorder=11)
        ax.add_patch(r)
        ax.text(box_x + 0.01 + (i-1)*seg_w + seg_w/2, box_y + 0.035, str(i), 
                transform=ax.transAxes, color='white', fontsize=8, ha='center', zorder=11)

    ax.text(box_x + 0.01, box_y + 0.01, f"LEVEL {judgment_level}: {status_text}", 
            transform=ax.transAxes, color=status_color, fontsize=11, fontweight='bold', zorder=11)

    # ==========================================
    # 4. SAVE TO DESKTOP
    # ==========================================
    ax.set_title("ALPHA SWARM: S&P 500 (Zoom Module V6)", fontsize=16, color='white', fontweight='bold', pad=20)
    ax.grid(True, color='gray', alpha=0.2)
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    plt.tight_layout()

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    filename = "Alpha_Swarm_Chart_V6_Zoom.png"
    full_path = os.path.join(desktop, filename)

    print(f"Saving file to Desktop: {full_path}...")
    plt.savefig(full_path)
    print(f"\n[SUCCESS] Image saved successfully!")
    print(f"CHECK YOUR DESKTOP FOR: {filename}")

except Exception as e:
    print(f"\nERROR: {e}")

print("\nPress ENTER key to close this window...")
input()