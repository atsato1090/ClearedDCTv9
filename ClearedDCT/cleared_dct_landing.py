import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="ClearedDCT",
    page_icon="✈️",
    layout="centered"
)

# Centered logo display
st.image("logo_loading.png", use_container_width=True)

# Optional app title under logo (remove if not needed)
st.markdown("<h2 style='text-align: center;'>Welcome to ClearedDCT</h2>", unsafe_allow_html=True)

# Spacing
st.markdown("##")

# Centered Enter App button
enter_app = st.button("🚀 Enter App", use_container_width=True)

if enter_app:
    # Attempt to switch to your main ClearedDCT app
    try:
        st.switch_page("pages/1_ClearedDCT_App.py")  # Ensure your app is in pages/ with this exact name
    except Exception as e:
        st.error(f"Unable to load ClearedDCT app. Error: {e}")
        st.stop()
