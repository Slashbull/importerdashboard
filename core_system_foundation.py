import streamlit as st
import pandas as pd

# ---- Basic Core System Foundation ---- #

# ---- User Authentication ---- #
USERS = {"admin": "admin123"}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    """User login system."""
    st.title("🔒 Secure Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("🚀 Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("🚨 Invalid Username or Password")

def logout():
    """Logs out the user."""
    st.session_state["authenticated"] = False
    st.rerun()

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ---- File Upload ---- #
st.title("📂 Upload Your Data")
uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"])

df = None
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")
    st.write("### 📊 Raw Data Preview")
    st.dataframe(df.head())

# Logout Button
st.sidebar.button("🔓 Logout", on_click=logout)

# Save file as core_system_foundation.py
