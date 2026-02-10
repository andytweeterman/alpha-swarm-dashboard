## 2026-02-09 - Accessible Colors for Status Badges
**Learning:** Standard CSS colors like "yellow" and "green" (#00CC00) often fail WCAG contrast requirements when used with white text. Specifically, "yellow" with white text is nearly invisible (1.07:1 ratio), and standard "green" is also poor (2.18:1).
**Action:** Always use specific, accessible hex codes for status indicators (e.g., `#1f7a1f` for green, `#b38600` for yellow/gold) and verify contrast ratios against the text color (usually white or black).
