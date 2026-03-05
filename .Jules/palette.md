## 2026-02-10 - Custom Components in Streamlit
**Learning:** Custom HTML components injected via `st.markdown(unsafe_allow_html=True)` often lack semantic structure (like `role` or `aria-label`), making them invisible or confusing to screen readers.
**Action:** When creating custom visual components (like cards or badges) using raw HTML in Streamlit, always include `role="group"` and `aria-label` to provide context.

## 2026-02-15 - CSS Variables for Custom HTML
**Learning:** Hardcoded hex colors in custom HTML strings break light/dark mode adaptability and can fail contrast checks.
**Action:** Define theme-aware colors in `styles.py` and inject them as CSS variables (`var(--color)`) for use in raw HTML strings.

## 2026-03-05 - Semantic Roles for Custom Pills
**Learning:** Custom HTML status pills or badges (like `.gov-pill` and `.premium-pill`) are read by screen readers as plain text without context, leading to confusion about their purpose.
**Action:** Always add semantic roles (e.g., `role="status"`) and descriptive `aria-label`s to custom status elements to ensure screen readers announce their context clearly to users.
