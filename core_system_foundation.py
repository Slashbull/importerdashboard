import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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

# ==================== GOOGLE SHEETS DATA HANDLING ====================
st.title("Importer Dashboard - Google Sheets Data Processing")

gsheet_url = st.text_input("Enter Google Sheets Link (Editor Access Required)")

def load_google_sheets(url):
    """Load data from Google Sheets into a Pandas DataFrame."""
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(sheet_url)
        return df
    except Exception as e:
        st.error("Error loading Google Sheet. Check the link and permissions.")
        return None

def write_to_google_sheets(df, url):
    """Write processed data to the 'Processed Data' sheet in Google Sheets."""
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet("Processed Data")
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("✅ Processed data successfully written to Google Sheets.")
    except Exception as e:
        st.error("Error writing to Google Sheets. Ensure correct access and credentials.")

if gsheet_url:
    df = load_google_sheets(gsheet_url)
    if df is not None:
        st.write("### Raw Data Preview:")
        st.write(df.head(10))
        
        # ==================== DATA PROCESSING ====================
        if "Quantity" in df.columns:
            df["Quantity"] = df["Quantity"].astype(str).str.replace("[^0-9]", "", regex=True).astype(float)
            df["Quantity_Tons"] = df["Quantity"] / 1000
        
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        if "Month" in df.columns:
            df["Month_Num"] = df["Month"].map(month_map)
        
        st.write("### Processed Data Preview:")
        st.write(df.head(10))
        
        # Write processed data to Google Sheets
        write_to_google_sheets(df, gsheet_url)
    
    # Logout Button
    if st.sidebar.button("Logout"):
        logout()
