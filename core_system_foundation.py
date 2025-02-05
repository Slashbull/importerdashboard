import streamlit as st
import pandas as pd
import gspread
import hashlib
import time
import logging
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# ==================== LOGGING CONFIGURATION ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==================== LOGIN SYSTEM ====================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

USER_CREDENTIALS = {
    "admin": hash_password("importer@123")
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
            logging.info("User logged in successfully.")
        else:
            st.sidebar.error("❌ Invalid Credentials")
            logging.warning("Invalid login attempt.")

def logout():
    st.session_state.clear()
    st.experimental_rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ==================== DATA UPLOAD SYSTEM ====================
st.title("Importer Dashboard - Google Sheets Upload")

gsheet_url = st.text_input("Enter Google Sheets Link")

def hash_link(link):
    """Hash the link for secure caching."""
    return hashlib.sha256(link.encode()).hexdigest()

@st.cache_data(ttl=86400)  # Cache for one day
def cache_sheet_link(link):
    hashed_link = hash_link(link)
    timestamp = time.time()
    return {"hashed_link": hashed_link, "timestamp": timestamp}

# Function to load Google Sheets Data
def load_google_sheets(url):
    """Load data from Google Sheets."""
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(sheet_url)  # Read the Google Sheets data
        logging.info("Data loaded successfully from Google Sheets.")
        return df, sheet_id
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        logging.error(f"Failed to load Google Sheets data: {e}")
        return None, None

# Load data based on Google Sheets URL
with st.spinner("Loading data..."):
    if gsheet_url:
        df, sheet_id = load_google_sheets(gsheet_url)
        cached_data = cache_sheet_link(gsheet_url)
    else:
        df, sheet_id = None, None

if df is not None:
    st.write("### Raw Data Preview:")
    st.write(df.head(10))
    
    # ==================== DATA CLEANING & VALIDATION ====================
    if "Quantity" not in df.columns or "Month" not in df.columns:
        st.error("Missing required columns: 'Quantity' and/or 'Month'")
        logging.warning("Data does not contain required columns.")
    else:
        # Convert Quantity column to numeric and auto-generate Tons
        try:
            df["Quantity"] = df["Quantity"].astype(str).str.replace("[^0-9]", "", regex=True).astype(float)
            df["Quantity_Tons"] = df["Quantity"] / 1000
        except ValueError:
            st.error("Quantity column contains non-numeric values. Please check your data.")
            logging.warning("Quantity column contains invalid data.")

        # Convert Month column to numeric format
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        if "Month" in df.columns:
            df["Month_Num"] = df["Month"].map(month_map)

        st.write("### Processed Data Preview:")
        st.write(df.head(10))

        # ==================== WRITE PROCESSED DATA TO "Processed Data" SHEET ====================
        try:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(sheet_id)
            try:
                processed_sheet = spreadsheet.worksheet("Processed Data")
            except gspread.exceptions.WorksheetNotFound:
                processed_sheet = spreadsheet.add_worksheet(title="Processed Data", rows="1000", cols="20")

            # Write processed data to the "Processed Data" sheet
            processed_sheet.clear()
            processed_sheet.update([df.columns.values.tolist()] + df.values.tolist())
            logging.info("Processed data written to the 'Processed Data' sheet.")
        except Exception as e:
            st.error(f"Failed to write processed data to the spreadsheet: {e}")
            logging.error(f"Error writing data to 'Processed Data' sheet: {e}")
else:
    st.error("No valid Google Sheets link provided. Please enter a valid Google Sheets URL.")
