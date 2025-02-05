import streamlit as st
import pandas as pd
import hashlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# ==================== GOOGLE SHEETS INTEGRATION ====================
st.title("Importer Dashboard - Google Sheets Data Processing")

gsheet_url = st.text_input("Enter Google Sheets Link")

# Google Sheets API Credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

def load_google_sheets(url):
    """Load data from Google Sheets and store in 'Processed Data' sheet."""
    sheet_id = url.split("/d/")[1].split("/")[0]
    spreadsheet = client.open_by_key(sheet_id)
    raw_data = pd.DataFrame(spreadsheet.sheet1.get_all_records())
    
    # Standardize column names
    column_mapping = {
        "Quanity": "Quantity",
        "Month ": "Month"
    }
    raw_data.rename(columns=column_mapping, inplace=True)
    
    # Process Data
    if "Quantity" in raw_data.columns:
        raw_data["Quantity"] = raw_data["Quantity"].astype(str).str.replace("[^0-9]", "", regex=True).astype(float)
        raw_data["Quantity_Tons"] = raw_data["Quantity"] / 1000
    
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    if "Month" in raw_data.columns:
        raw_data["Month_Num"] = raw_data["Month"].map(month_map)
    
    # Store processed data in a new sheet
    try:
        processed_sheet = spreadsheet.worksheet("Processed Data")
        spreadsheet.del_worksheet(processed_sheet)
    except:
        pass  # Sheet doesn't exist, continue
    
    processed_sheet = spreadsheet.add_worksheet(title="Processed Data", rows=str(len(raw_data)+1), cols=str(len(raw_data.columns)))
    processed_sheet.update([raw_data.columns.values.tolist()] + raw_data.values.tolist())
    
    return raw_data

if gsheet_url:
    df = load_google_sheets(gsheet_url)
else:
    df = None

if df is not None:
    st.write("### Processed Data Stored in Google Sheets")
    st.write(df.head(10))
    
    # Logout Button
    if st.sidebar.button("Logout"):
        logout()
