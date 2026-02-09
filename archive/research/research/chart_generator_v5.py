import sys
import os

try:
    print("--- [STARTING CHART GENERATOR V5: FORCE ZOOM] ---")
    
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import pandas as pd

    # ==========================================
    # 1. HIGH VOLATILITY SYNTHETIC DATA
    # ==========================================
    print("Generating HIGH VOLATILITY data...")
    np.random.seed(42)
    n_history = 60
    n_forecast = 20
    start_price = 5800

    dates = pd.date_range(end=pd.Timestamp.today(), periods=n_history + n_forecast, freq='B')
    
    closes = np.zeros(n_history)
    opens = np.zeros(n_history)
    highs = np.zeros(n_history)
    lows = np.zeros(n_history)
    closes[0] = start_price

    # TRIPLE VOLATILITY so the chart looks jagged/exciting
    for i in range(1, n_history):
        change = np.random.normal(0, 60) # Huge swings
        closes[i] = closes[i-1] + change
        opens[i] = closes[i-1] + np.random.normal(0, 20) # Gaps
        
        # Make wicks large
        noise_high = abs(np.random.normal(0, 30))
        noise_low = abs(np.random.normal(0, 30))
        highs[i] = max(opens[i], closes[i]) + noise_high
        lows[i] = min(opens[i], closes[i]) - noise_low

    n_sims = 100
    simulations = np.zeros((n_forecast, n_sims))
    simulations[0, :] = closes[-1]

    for t in range(1, n_forecast):
        drift = 2.0 
        shock = np.random.normal(0, 50, n_sims) # High forecast volatility
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

    # --- AGGRESSIVE ZOOM LOGIC ---
    # Find the absolute lowest and highest pixels in the entire dataset
    all_data_points = np.concatenate([highs, lows, upper_bound.flatten(), lower_bound.flatten()])
    y_min_val = np.min(all_data_points)
    y_max_val = np.max(all_data_points)
    
    # Debug print
    print(f"DATA RANGE: Low={y_min_val:.2f}, High={y_max_val:.2f}")

    # Set Tight Limits (Only 1% padding)
    ax.set_ylim(y_min_val * 0.99, y_max_val * 1.01)
    # -----------------------------

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
    ax.set_title("ALPHA SWARM: S&P 500 PROJECTION (Module V5 - High Volatility)", fontsize=16, color='white', fontweight='bold', pad=20)
    ax.grid(True, color='gray', alpha=0.2)
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    plt.tight_layout()

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    filename = "Alpha_Swarm_Chart_V5.png"
    full_path = os.path.join(desktop, filename)

    print(f"Saving file to Desktop: {full_path}...")
    plt.savefig(full_path)
    print(f"\n[SUCCESS] Image saved successfully!")
    print(f"CHECK YOUR DESKTOP FOR: {filename}")

except Exception as e:
    print(f"\nERROR: {e}")

print("\nPress ENTER key to close this window...")
input()