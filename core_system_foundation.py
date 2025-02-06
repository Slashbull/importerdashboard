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

# ---- File Upload or Google Sheet Link ---- #
st.title("📂 Upload Your Data")
upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"))

df = None
if upload_option == "Upload CSV":
    uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")

elif upload_option == "Google Sheet Link":
    sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
    if sheet_url:
        try:
            df = pd.read_csv(sheet_url)  # Assumes public Google Sheet as CSV format
            st.success("✅ Google Sheet loaded successfully!")
        except Exception as e:
            st.error(f"🚨 Error loading Google Sheet: {e}")

if df is not None:
    st.write("### 📊 Raw Data Preview")
    st.dataframe(df.head())

# Logout Button
st.sidebar.button("🔓 Logout", on_click=logout)

# Save file as core_system_foundation.py
