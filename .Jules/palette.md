# PALETTE'S JOURNAL - CRITICAL LEARNINGS ONLY

## 2026-06-05 - Streamlit Radio Button Context
**Learning:** Streamlit's `st.radio` widget supports a `help` parameter that adds a question mark tooltip next to the label. This is a subtle but effective way to provide context for complex options or explain why certain features (like "Premium" tiers) are disabled, without cluttering the UI with extra text.
**Action:** Always check for `help` parameters on Streamlit input widgets to add explanatory micro-copy, especially for disabled or complex controls.

## 2026-06-05 - Native Components vs Custom HTML
**Learning:** Replacing custom HTML/CSS badges (div soup) with native Streamlit status components (`st.success`, `st.warning`, `st.error`) not only fixes XSS vulnerabilities but significantly improves accessibility by providing semantic roles and standard keyboard navigation, without sacrificing much visual impact.
**Action:** Prioritize native Streamlit components over `st.markdown(unsafe_allow_html=True)` for status indicators and alerts.
