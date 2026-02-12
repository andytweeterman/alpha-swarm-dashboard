## 2026-02-24 - Custom HTML Components via Markdown
**Learning:** The application extensively uses `st.markdown(unsafe_allow_html=True)` to create custom components (e.g., Market Cards, Pills). These components lack semantic structure and ARIA labels by default, making them inaccessible to screen readers.
**Action:** When modifying or creating such components, always wrap them in semantic containers (e.g., `role="group"`) and add `aria-label` attributes to ensure content is perceivable and navigable.
