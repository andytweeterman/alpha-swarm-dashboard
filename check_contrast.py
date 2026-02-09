
def get_contrast_ratio(hex1, hex2):
    def get_luminance(hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

        def adjust(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    l1 = get_luminance(hex1)
    l2 = get_luminance(hex2)

    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)

colors = {
    "Normal (Green)": "#00CC00",
    "Watchlist (Yellow)": "#FFFF00",
    "Caution (Orange)": "#FFA500",
    "Emergency (Red)": "#FF0000",
    "Proposed Normal (#1f7a1f)": "#1f7a1f",
    "Proposed Watchlist (#b38600 - Dark Gold)": "#b38600",
    "Proposed Caution (#d35400 - Pumpkin)": "#d35400",
    "Proposed Emergency (#c0392b - Pomegranate)": "#c0392b",
    "Better Green (#198754)": "#198754",
    "Better Watchlist (#856404)": "#856404", # Bootstrap warning text color
    "Better Caution (#fd7e14)": "#fd7e14",
    "Better Red (#dc3545)": "#dc3545",
}

print(f"{'Color':<40} | {'Contrast with White':<20} | {'Result'}")
print("-" * 75)
for name, hex_val in colors.items():
    ratio = get_contrast_ratio("#FFFFFF", hex_val)
    status = "✅ PASS (AA Large)" if ratio >= 3.0 else "❌ FAIL"
    if ratio >= 4.5: status = "✅ PASS (AA Normal)"
    print(f"{name:<40} | {ratio:.2f}:1              | {status}")
