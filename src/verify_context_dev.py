import streamlit as st
try:
    theme = st.context.theme
    print(f"Type of theme: {type(theme)}")
    print(f"Content of theme: {theme}")
    if hasattr(theme, 'base'):
        print(f"theme.base: {theme.base}")
    else:
        print("theme object has no base attribute")
        # Maybe it's a dict?
        if isinstance(theme, dict):
             print(f"theme keys: {theme.keys()}")
             if 'base' in theme:
                 print(f"theme['base']: {theme['base']}")
except Exception as e:
    print(f"Error: {e}")
