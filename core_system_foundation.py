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

# ==================== DATA UPLOAD SYSTEM ====================
st.title("Importer Dashboard - Google Sheets Upload")

gsheet_url = st.text_input("Enter Google Sheets Link")

# Function to load Google Sheets Data
def load_google_sheets(url):
    """Load data from Google Sheets."""
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(sheet_url)  # Read the Google Sheets data
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return None

# Load data based on Google Sheets URL
if gsheet_url:
    df = load_google_sheets(gsheet_url)
else:
    df = None

# Display raw data if available
if df is not None:
    st.write("### Raw Data Preview:")
    st.write(df.head(10))
    
    # ==================== DATA CLEANING & PROCESSING ====================
    if "Quantity" in df.columns:
        # Convert Quantity column to numeric and auto-generate Tons
        df["Quantity"] = df["Quantity"].astype(str).str.replace("[^0-9]", "", regex=True).astype(float)
        df["Quantity_Tons"] = df["Quantity"] / 1000
    
    # Convert Month column to numeric format
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    if "Month" in df.columns:
        df["Month_Num"] = df["Month"].map(month_map)
    
    # Display processed data
    st.write("### Processed Data Preview:")
    st.write(df.head(10))
    
    # ==================== FILTER SYSTEM ====================
    st.sidebar.subheader("Filters")
    years = df["Year"].dropna().astype(str).unique().tolist()
    states = df["Consignee State"].dropna().astype(str).unique().tolist()
    suppliers = df["Exporter"].dropna().astype(str).unique().tolist()
    consignees = df["Consignee"].dropna().astype(str).unique().tolist()
    months = df["Month"].dropna().astype(str).unique().tolist()
    
    selected_years = st.sidebar.multiselect("Select Year", ["All"] + years, default=["All"])
    selected_states = st.sidebar.multiselect("Select Consignee State", ["All"] + states, default=["All"])
    selected_suppliers = st.sidebar.multiselect("Select Exporter", ["All"] + suppliers, default=["All"])
    selected_consignees = st.sidebar.multiselect("Select Consignee", ["All"] + consignees, default=["All"])
    selected_months = st.sidebar.multiselect("Select Month", ["All"] + months, default=["All"])
    
    # Filter data based on selected filters
    def filter_data(df, selected_years, selected_states, selected_suppliers, selected_consignees, selected_months):
        filtered_df = df.copy()
        if "All" not in selected_years:
            filtered_df = filtered_df[filtered_df["Year"].astype(str).isin(selected_years)]
        if "All" not in selected_states:
            filtered_df = filtered_df[filtered_df["Consignee State"].astype(str).isin(selected_states)]
        if "All" not in selected_suppliers:
            filtered_df = filtered_df[filtered_df["Exporter"].astype(str).isin(selected_suppliers)]
        if "All" not in selected_consignees:
            filtered_df = filtered_df[filtered_df["Consignee"].astype(str).isin(selected_consignees)]
        if "All" not in selected_months:
            filtered_df = filtered_df[filtered_df["Month"].astype(str).isin(selected_months)]
        return filtered_df
    
    filtered_df = filter_data(df, selected_years, selected_states, selected_suppliers, selected_consignees, selected_months)
    
    st.write("### Filtered Data Preview:")
    st.write(filtered_df.head(10))
    
    # ==================== UNIT SELECTION ====================
    if "Quantity" in filtered_df.columns and "Quantity_Tons" in filtered_df.columns:
        unit = st.radio("Select Unit", ["Kgs", "Tons"], horizontal=True)
        display_column = "Quantity_Tons" if unit == "Tons" else "Quantity"
        st.write("### Displaying in:", unit)
        st.dataframe(filtered_df[[display_column]])
    
    # ==================== EXPORT SYSTEM ====================
    st.sidebar.subheader("Export Data")
    export_format = st.sidebar.radio("Select Export Format", ["CSV", "Excel"])
    
    if st.sidebar.button("Download Filtered Data"):
        if export_format == "CSV":
            filtered_df.to_csv("filtered_data.csv", index=False)
            st.sidebar.download_button(label="Download CSV", data=open("filtered_data.csv", "rb"), file_name="filtered_data.csv", mime="text/csv")
        elif export_format == "Excel":
            filtered_df.to_excel("filtered_data.xlsx", index=False)
            st.sidebar.download_button(label="Download Excel", data=open("filtered_data.xlsx", "rb"), file_name="filtered_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # ==================== LOGOUT ====================
    if st.sidebar.button("Logout"):
        logout()
else:
    st.error("No valid Google Sheets link provided. Please enter a valid Google Sheets URL.")
