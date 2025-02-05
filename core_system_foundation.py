import streamlit as st
import pandas as pd
import hashlib

# ==================== LOGIN SYSTEM ====================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Dummy user credentials (Can be expanded for multi-user authentication)
USER_CREDENTIALS = {
    "admin": hash_password("importer@123")  # Change this password securely
}

def authenticate_user(username, password):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == hash_password(password):
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        return True
    return False

def logout():
    st.session_state.clear()
    st.rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.sidebar.header("🔐 Login to Access Dashboard")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate_user(username, password):
            st.sidebar.success("✅ Login Successful!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid Credentials")
    st.stop()

# ==================== DATA UPLOAD SYSTEM ====================
st.title("Importer Dashboard")
if "data_uploaded" not in st.session_state:
    st.session_state["data_uploaded"] = False

if not st.session_state["data_uploaded"]:
    st.subheader("Upload Data to Proceed")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
    gsheet_url = st.text_input("Enter Google Sheets Link (Optional)")

    @st.cache_data
    def load_data(file):
        """Load CSV or Excel data into a Pandas DataFrame with optimized error handling."""
        try:
            with st.spinner("📂 Loading Data... Please wait."):
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file, low_memory=False)
                else:
                    df = pd.read_excel(file)
                
                column_mapping = {"Quanity": "Quantity", "Month ": "Month"}
                df.rename(columns=column_mapping, inplace=True)
                return df
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            return None

    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            if "Quantity" in df.columns:
                df["Quantity_Tons"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0) / 1000
            st.session_state["filtered_data"] = df.copy()
            st.session_state["data_uploaded"] = True
            st.rerun()
    st.stop()

# ==================== DASHBOARD SELECTION ====================
st.sidebar.header("Select Dashboard")
dashboard_choice = st.sidebar.radio("Choose Dashboard", ["Market Overview", "Competitor Insights"])

if dashboard_choice == "Market Overview":
    import market_overview_dashboard  # Loads Market Overview separately
elif dashboard_choice == "Competitor Insights":
    import competitor_insights_dashboard  # Loads Competitor Insights separately

# Logout Button
if st.sidebar.button("Logout"):
    logout()
