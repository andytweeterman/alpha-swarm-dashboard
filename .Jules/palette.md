## 2026-02-10 - Custom Components in Streamlit
**Learning:** Custom HTML components injected via `st.markdown(unsafe_allow_html=True)` often lack semantic structure (like `role` or `aria-label`), making them invisible or confusing to screen readers.
**Action:** When creating custom visual components (like cards or badges) using raw HTML in Streamlit, always include `role="group"` and `aria-label` to provide context.

## 2026-02-15 - CSS Variables for Custom HTML
**Learning:** Hardcoded hex colors in custom HTML strings break light/dark mode adaptability and can fail contrast checks.
**Action:** Define theme-aware colors in `styles.py` and inject them as CSS variables (`var(--color)`) for use in raw HTML strings.

## 2026-02-26 - Dynamic Text Contrast
**Learning:** Hardcoded white text on status indicators (like "COMFORT ZONE" green) fails WCAG contrast requirements when the background color is light.
**Action:** Implement a `get_best_text_color` helper function that calculates relative luminance and returns either black or white text color dynamically based on the background color.
