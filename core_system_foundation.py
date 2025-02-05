import streamlit as st
import pandas as pd
import streamlit_oauth as st_oauth
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ==================== GOOGLE OAUTH AUTHENTICATION ====================
CLIENT_ID = "your-client-id.apps.googleusercontent.com"
CLIENT_SECRET = "your-client-secret"
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Streamlit OAuth2 setup
oauth = st_oauth.OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorization_url=AUTHORIZATION_URL,
    token_url=TOKEN_URL,
    redirect_uri="https://slashbull-importerdashboard-core-system-foundation-kfmlgw.streamlit.app/"
)

if "token" not in st.session_state:
    token = oauth.get_token()
    if token:
        st.session_state["token"] = token

if "token" not in st.session_state:
    st.warning("🔐 Please log in with Google to access your Google Sheets.")
    st.stop()

# ==================== GOOGLE SHEETS FUNCTIONS ====================
def get_gspread_service():
    creds = service_account.Credentials.from_authorized_user_info(st.session_state["token"], SCOPES)
    service = build("sheets", "v4", credentials=creds)
    return service

def load_google_sheets(sheet_url):
    try:
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        service = get_gspread_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range="Sheet1").execute()
        data = result.get("values", [])
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        st.error(f"Error loading Google Sheets data: {e}")
        return None

def save_to_google_sheets(sheet_url, df):
    try:
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        service = get_gspread_service()
        sheet = service.spreadsheets()
        values = [df.columns.tolist()] + df.values.tolist()
        sheet.values().update(
            spreadsheetId=sheet_id,
            range="ProcessedData!A1",
            valueInputOption="RAW",
            body={"values": values},
        ).execute()
        st.success("✅ Processed data saved successfully to Google Sheets!")
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ==================== STREAMLIT DASHBOARD ====================
st.title("Importer Dashboard - Google Sheets Processing")
gsheet_url = st.text_input("Enter Google Sheets Link")

df = None
if gsheet_url:
    df = load_google_sheets(gsheet_url)

if df is not None:
    st.write("### Raw Data Preview:")
    st.write(df.head(10))
    
    # Processing logic here (similar to your existing code)
    if "Quantity" in df.columns:
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
        df["Quantity_Tons"] = df["Quantity"] / 1000
    
    # Save processed data back to Google Sheets
    if st.button("Save Processed Data to Google Sheets"):
        save_to_google_sheets(gsheet_url, df)
