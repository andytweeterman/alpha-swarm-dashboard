## 2026-02-04 - Accessible Streamlit Custom Components
**Learning:** Custom UI components built with `st.markdown` (like cards or badges) are completely invisible to screen readers as semantic groups. They often read as disparate text elements.
**Action:** Always wrap custom HTML components in a container with `role="group"` and an `aria-label` that summarizes the content, and use `aria-hidden="true"` on the individual decorative children to reduce noise.
