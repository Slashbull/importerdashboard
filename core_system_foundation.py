import streamlit as st
import pandas as pd
import hashlib

# ---- Phase 1: Core System Foundation ---- #

# ---- User Authentication ---- #
USERS = {"admin": "admin123"}  # Future enhancement: Store securely

def hash_password(password: str) -> str:
    """Hash passwords using SHA-256 for security."""
    return hashlib.sha256(password.encode()).hexdigest()

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

# ---- File Upload & Data Preprocessing ---- #
st.title("📂 Importer Decision-Making Dashboard")

upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"))

df = None
if upload_option == "Upload CSV":
    uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

elif upload_option == "Google Sheet Link":
    sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
    if sheet_url:
        df = pd.read_csv(sheet_url)  # Assumes public Google Sheet as CSV format

if df is not None:
    try:
        # Ensure required columns exist
        required_columns = ["SR NO.", "Job No.", "Consignee", "Exporter", "Mark", "Quanity (Kgs)", "Quanity (Tons)", "Month", "Year", "Consignee State"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"🚨 Missing Columns: {missing_columns}")
            st.stop()
        
        # Data Cleaning
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                     "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        df["Quanity (Kgs)"] = df["Quanity (Kgs)"].astype(str).str.replace(" Kgs", "").astype(float)
        df["Quanity (Tons)"] = df["Quanity (Tons)"].astype(str).str.replace(" tons", "").astype(float)
        df["Month"] = df["Month"].map(month_map)
        
        # Remove exact duplicate rows
        df = df.drop_duplicates()
        
        st.success("✅ Data successfully processed!")
        
        # Display Processed Data
        st.write("### 📊 Processed Data Preview")
        st.dataframe(df.head())
    
    except Exception as e:
        st.error(f"🚨 Error processing file: {e}")

# Logout Button
st.sidebar.button("🔓 Logout", on_click=logout)

# Save file as core_system_foundation.py
