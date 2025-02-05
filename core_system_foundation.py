import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
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
    """Load data from Google Sheets into a Pandas DataFrame using direct access."""
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(sheet_url)
        return df
    except Exception as e:
        st.error("❌ Error loading Google Sheet. Check the link and permissions.")
        return None

def write_to_google_sheets(df, url):
    """Write processed data to 'Processed Data' sheet directly without API key."""
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        gc = gspread.oauth()  # Authenticate using direct Google OAuth (no JSON required)
        sheet = gc.open_by_key(sheet_id)

        # Check if "Processed Data" sheet exists, if not create it
        try:
            worksheet = sheet.worksheet("Processed Data")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title="Processed Data", rows="1000", cols="20")

        worksheet.clear()
        set_with_dataframe(worksheet, df)
        st.success("✅ Data successfully written to Google Sheets!")
    except Exception as e:
        st.error("❌ Error writing to Google Sheets. Ensure correct access and permissions.")

# ==================== PROCESSING DATA ====================
if gsheet_url:
    df = load_google_sheets(gsheet_url)
    if df is not None:
        st.write("### Raw Data Preview:")
        st.write(df.head(10))

        # Convert Quantity column to numeric and auto-generate Tons
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
