import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

print("--- GENERATING DASHBOARD MOCKUP ---")

# ==========================================
# 1. SETUP THE CANVAS
# ==========================================
# We create a small canvas just to show the UI Element
fig, ax = plt.subplots(figsize=(8, 4))
ax.set_facecolor('black')
fig.patch.set_facecolor('black')

# Hide axes
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# ==========================================
# 2. DRAW THE MAIN GOVERNANCE BADGE (The Parent)
# ==========================================
# This is the "Avalanche" Logic (Credit/VIX)
# Let's say Credit is fine, so it's "NORMAL OPS" (Level 3)
box_x, box_y = 0.1, 0.55
box_w, box_h = 0.8, 0.35

# Main Frame
rect = patches.FancyBboxPatch((box_x, box_y), box_w, box_h, boxstyle="round,pad=0.02", 
                              fc='#1a1a1a', ec='cyan', linewidth=2, transform=ax.transAxes)
ax.add_patch(rect)

# Title
ax.text(0.5, 0.82, "SWARM GOVERNANCE: LEVEL 3", 
        transform=ax.transAxes, color='cyan', fontsize=16, fontweight='bold', ha='center')

# Status Text
ax.text(0.5, 0.65, "SYSTEMIC PLUMBING STABLE", 
        transform=ax.transAxes, color='white', fontsize=12, ha='center')

# ==========================================
# 3. DRAW THE "HORIZON STRIP" (The Dad Request)
# ==========================================
# This solves the "Short term good / Long term bad" conflict.
# We create 3 distinct zones below the main badge.

# Y-position for the strip
strip_y = 0.15
strip_h = 0.3
gap = 0.05
width = (box_w - (2 * gap)) / 3

# --- 1 WEEK (MOMENTUM) ---
# Scenario: Market is rallying (Green)
x1 = box_x
p1 = patches.Rectangle((x1, strip_y), width, strip_h, fc='#004d00', ec='#00ff00', transform=ax.transAxes)
ax.add_patch(p1)
ax.text(x1 + width/2, strip_y + 0.18, "1 WEEK", color='white', fontsize=10, ha='center', fontweight='bold')
ax.text(x1 + width/2, strip_y + 0.08, "BULLISH", color='#00ff00', fontsize=12, ha='center', fontweight='bold')
# Icon (Simple Arrow Up)
ax.text(x1 + width/2, strip_y + 0.02, "▲", color='#00ff00', fontsize=16, ha='center')

# --- 1 MONTH (TRANSITION) ---
# Scenario: Stalling (Yellow)
x2 = x1 + width + gap
p2 = patches.Rectangle((x2, strip_y), width, strip_h, fc='#4d4d00', ec='#ffff00', transform=ax.transAxes)
ax.add_patch(p2)
ax.text(x2 + width/2, strip_y + 0.18, "1 MONTH", color='white', fontsize=10, ha='center', fontweight='bold')
ax.text(x2 + width/2, strip_y + 0.08, "NEUTRAL", color='#ffff00', fontsize=12, ha='center', fontweight='bold')
ax.text(x2 + width/2, strip_y + 0.02, "▬", color='#ffff00', fontsize=16, ha='center')

# --- 6 MONTHS (STRUCTURAL) ---
# Scenario: The Trap (Red) - This is what Dad is worried about
x3 = x2 + width + gap
p3 = patches.Rectangle((x3, strip_y), width, strip_h, fc='#4d0000', ec='#ff0000', transform=ax.transAxes)
ax.add_patch(p3)
ax.text(x3 + width/2, strip_y + 0.18, "6 MONTHS", color='white', fontsize=10, ha='center', fontweight='bold')
ax.text(x3 + width/2, strip_y + 0.08, "BEARISH", color='#ff0000', fontsize=12, ha='center', fontweight='bold')
ax.text(x3 + width/2, strip_y + 0.02, "▼", color='#ff0000', fontsize=16, ha='center')

# ==========================================
# 4. SAVE
# ==========================================
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
save_path = os.path.join(desktop, "Dashboard_Concept.png")
plt.savefig(save_path)

print(f"[SUCCESS] Mockup saved to: {save_path}")
print("Send this image to Dad. It shows how to visualize the 'Time Horizon Conflict'.")