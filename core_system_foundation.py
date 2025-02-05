import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# ==================== GOOGLE AUTH & SHEETS ACCESS ====================

# Load Google Service Account Credentials
@st.cache_resource
def get_gspread_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(credentials)

gc = get_gspread_client()

# Function to open or create Google Sheet
def get_or_create_sheet(sheet_url, sheet_name="Processed Data"):
    try:
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        sh = gc.open_by_key(sheet_id)
        try:
            worksheet = sh.worksheet(sheet_name)
        except:
            worksheet = sh.add_worksheet(title=sheet_name, rows="1000", cols="20")
        return worksheet
    except Exception as e:
        st.error(f"Error accessing Google Sheets: {e}")
        return None

# ==================== STREAMLIT UI ====================
st.title("Importer Dashboard - Google Sheets Integration")

gsheet_url = st.text_input("Enter Google Sheets Link")
if gsheet_url:
    worksheet = get_or_create_sheet(gsheet_url)
else:
    worksheet = None

# Load data from Google Sheets
def load_google_sheets(worksheet):
    try:
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_google_sheets(worksheet) if worksheet else None

# Display data preview
if df is not None and not df.empty:
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

    # ==================== WRITE BACK TO GOOGLE SHEETS ====================
    if st.button("Save Processed Data to Google Sheets"):
        try:
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            st.success("✅ Data successfully saved to Google Sheets!")
        except Exception as e:
            st.error(f"❌ Error writing to Google Sheets: {e}")
else:
    st.warning("No data found. Please enter a valid Google Sheets link.")
