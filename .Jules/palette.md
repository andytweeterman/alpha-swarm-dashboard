## 2026-02-10 - Custom Components in Streamlit
**Learning:** Custom HTML components injected via `st.markdown(unsafe_allow_html=True)` often lack semantic structure (like `role` or `aria-label`), making them invisible or confusing to screen readers.
**Action:** When creating custom visual components (like cards or badges) using raw HTML in Streamlit, always include `role="group"` and `aria-label` to provide context.

## 2026-02-15 - CSS Variables for Custom HTML
**Learning:** Hardcoded hex colors in custom HTML strings break light/dark mode adaptability and can fail contrast checks.
**Action:** Define theme-aware colors in `styles.py` and inject them as CSS variables (`var(--color)`) for use in raw HTML strings.

## 2026-02-28 - Dynamic Text Contrast
**Learning:** Fixed status badges where white text on bright backgrounds (Yellow/Orange) failed WCAG contrast checks. Background colors are dynamic (e.g., from an API or calculation), so text color must also be dynamic.
**Action:** Use a `get_best_text_color(hex_bg)` utility to calculate the accessible text color (black/white) at runtime and inject it via inline styles. Always ensure `role="status"` is present for status indicators.
