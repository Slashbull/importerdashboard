import streamlit as st

# ---- Navigation System ---- #
SECTIONS = {
    "Market Overview": "View market trends and insights",
    "Competitor Insights": "Analyze competitor performance",
    "Processed Data Download": "Download processed datasets",
    "Settings": "Manage system preferences and configurations"
}

def set_navigation_ui():
    """ Apply global UI styles for a modern navigation experience """
    st.markdown("""
    <style>
        .stButton>button {width: 100%; border-radius: 8px; padding: 10px;}
        .stSelectbox>div>div>select {text-align: center;}
        .css-1d391kg {text-align: center;}
        .stSidebar {background-color: #f8f9fa; padding: 10px; border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True)

def show_navigation():
    """ Display the sidebar navigation menu """
    set_navigation_ui()
    st.sidebar.title("🧭 Navigation")
    selected_section = st.sidebar.radio("Choose Section:", list(SECTIONS.keys()), format_func=lambda x: f"📌 {x}")
    st.session_state["current_screen"] = selected_section
    
    st.sidebar.markdown(f"**ℹ️ {SECTIONS[selected_section]}**")
    
    if selected_section == "Settings":
        show_settings()
    return selected_section

def show_settings():
    """ Display system settings page """
    st.title("⚙️ Settings")
    st.subheader("Customize your dashboard experience")
    theme = st.radio("Choose Theme:", ["Light", "Dark"], key="theme_selection")
    st.session_state["theme"] = theme
    st.success("✅ Settings updated successfully!")

# Save file as navigation.py
