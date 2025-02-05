import streamlit as st
from pathlib import Path

# ---- Authentication System ---- #
USERS = {"admin": "admin123"}  # Hardcoded for now (can be extended to a DB later)

# ---- Session State Initialization ---- #
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ---- UI Styling ---- #
def set_ui():
    st.markdown("""
    <style>
        .css-1d391kg {text-align: center;}
        .stButton>button {width: 100%; border-radius: 8px; padding: 10px;}
        .stTextInput>div>div>input {text-align: center;}
    </style>
    """, unsafe_allow_html=True)

# ---- Login Function ---- #
def login():
    set_ui()
    st.title("🔒 Secure Login")
    st.subheader("Welcome to the Importer Dashboard")
    st.markdown("Please enter your credentials to access the system.")
    
    username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_password")
    
    if st.button("🚀 Login", use_container_width=True):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("🚨 Invalid Username or Password")

# ---- Logout Function ---- #
def logout():
    st.session_state["authenticated"] = False
    st.rerun()

# ---- Authentication Middleware ---- #
def authentication_required():
    if not st.session_state["authenticated"]:
        login()
        st.stop()

# ---- Security Best Practices ---- #
def store_user_credentials():
    """
    Future Enhancement: Store and encrypt user credentials securely
    instead of using hardcoded credentials.
    """
    pass

# Save file as authentication.py
