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

def login():
    st.sidebar.header("🔐 Login to Access Dashboard")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate_user(username, password):
            st.sidebar.success("✅ Login Successful!")
        else:
            st.sidebar.error("❌ Invalid Credentials")

def logout():
    st.session_state.clear()
    st.experimental_rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ==================== UI LAYOUT & NAVIGATION ====================
st.title("Importer Dashboard")
tabs = st.tabs(["📂 Data Upload", "📊 Market Overview"])

with tabs[0]:
    # ==================== DATA UPLOAD SYSTEM ====================
    st.subheader("Upload & Process Data")
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

    @st.cache_data
    def load_google_sheets(url):
        """Load data from Google Sheets with better error handling."""
        try:
            with st.spinner("📂 Fetching Data from Google Sheets... Please wait."):
                sheet_id = url.split("/d/")[1].split("/")[0]
                sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                df = pd.read_csv(sheet_url)
            return df
        except Exception as e:
            st.error(f"❌ Failed to load Google Sheets data: {e}")
            return None

    if uploaded_file:
        df = load_data(uploaded_file)
    elif gsheet_url:
        df = load_google_sheets(gsheet_url)
    else:
        df = None

    if df is not None:
        st.write("### Raw Data Preview:")
        st.write(df.head(10))
        
        # ==================== DATA CLEANING & PROCESSING ====================
        if "Quantity" in df.columns:
            df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
            df["Quantity_Tons"] = df["Quantity"] / 1000
        
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        if "Month" in df.columns:
            df["Month_Num"] = df["Month"].map(month_map)
        
        st.write("### Processed Data Preview:")
        st.write(df.head(10))
        
        # Store filtered data in session state
        st.session_state["filtered_data"] = df.copy()

with tabs[1]:
    # ==================== MARKET OVERVIEW SCREEN ====================
    st.subheader("Market Overview")
    if "filtered_data" in st.session_state:
        df = st.session_state["filtered_data"].copy()
        if "Quantity" in df.columns:
            st.write("### Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Imports (Kgs)", f"{df['Quantity'].sum():,.0f}")
            col2.metric("Top Importing State", df.groupby("Consignee State")["Quantity"].sum().idxmax())
            col3.metric("Top Exporter", df.groupby("Exporter")["Quantity"].sum().idxmax())
            
            st.write("### Monthly Import Trends")
            monthly_trends = df.groupby("Month")["Quantity"].sum().reset_index()
            st.line_chart(monthly_trends, x="Month", y="Quantity")
        else:
            st.error("Quantity column missing in the dataset.")
    else:
        st.error("No data available. Please upload a file in the Data Upload tab.")

# Logout Button
if st.sidebar.button("Logout"):
    logout()
