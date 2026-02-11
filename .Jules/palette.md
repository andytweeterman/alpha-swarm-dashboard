## 2024-05-24 - Streamlit Disabled Widget Context
**Learning:** `st.radio` supports `help` tooltips that remain interactive even when the widget itself is `disabled=True`. This is a critical pattern for "freemium" features where you want to show the option exists but is locked.
**Action:** Always attach a `help` parameter to disabled widgets explaining *why* it is disabled and how to unlock it.
