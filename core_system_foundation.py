import streamlit as st
import pandas as pd
import polars as pl
import hashlib

# ==================== LOGIN SYSTEM ====================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Dummy user credentials (Can be expanded for multi-user authentication)
USER_CREDENTIALS = {
    "admin": hash_password("importer@123")  # Change this password securely
}

def login():
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == hash_password(password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.sidebar.success("Login Successful!")
        else:
            st.sidebar.error("Invalid Credentials")

def logout():
    st.session_state.clear()
    st.experimental_rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ==================== DATA UPLOAD SYSTEM ====================
st.title("Importer Dashboard - Data Upload & Processing")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
gsheet_url = st.text_input("Enter Google Sheets Link (Optional)")

def load_data(file):
    """Load CSV or Excel data into a Polars DataFrame with proper column renaming."""
    if file.name.endswith(".csv"):
        df = pl.read_csv(file)
    else:
        df = pl.read_excel(file)
    
    # Standardize column names to remove typos and spaces
    column_mapping = {
        "Quanity": "Quantity",
        "Month ": "Month"
    }
    df = df.rename(column_mapping)
    return df

def load_google_sheets(url):
    """Load data from Google Sheets."""
    sheet_id = url.split("/d/")[1].split("/")[0]
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pl.read_csv(sheet_url)
    return df

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
    
    # Convert Quantity column to numeric (Kgs & Tons Toggle)
    if "Quantity" in df.columns:
        df = df.with_columns(
            pl.col("Quantity").str.replace_all("[^0-9]", "").cast(pl.Float64).alias("Quantity_Kgs")
        )
        df = df.with_columns(
            (pl.col("Quantity_Kgs") / 1000).alias("Quantity_Tons")
        )
    
    # Convert Month column to numeric format
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    if "Month" in df.columns:
        df = df.with_columns(
            pl.col("Month").replace(month_map).alias("Month_Num")
        )
    
    # Display cleaned data
    st.write("### Processed Data Preview:")
    st.write(df.head(10))
    
    # ==================== FILTER SYSTEM ====================
    st.sidebar.subheader("Filters")
    years = df["Year"].unique().to_list()
    states = df["Consignee State"].unique().to_list()
    suppliers = df["Exporter"].unique().to_list()
    consignees = df["Consignee"].unique().to_list()
    months = df["Month"].unique().to_list()
    
    selected_years = st.sidebar.multiselect("Select Year", ["All"] + years, default=["All"])
    selected_states = st.sidebar.multiselect("Select Consignee State", ["All"] + states, default=["All"])
    selected_suppliers = st.sidebar.multiselect("Select Exporter", ["All"] + suppliers, default=["All"])
    selected_consignees = st.sidebar.multiselect("Select Consignee", ["All"] + consignees, default=["All"])
    selected_months = st.sidebar.multiselect("Select Month", ["All"] + months, default=["All"])
    
    filtered_df = df
    if "All" not in selected_years:
        filtered_df = filtered_df.filter(pl.col("Year").is_in(selected_years))
    if "All" not in selected_states:
        filtered_df = filtered_df.filter(pl.col("Consignee State").is_in(selected_states))
    if "All" not in selected_suppliers:
        filtered_df = filtered_df.filter(pl.col("Exporter").is_in(selected_suppliers))
    if "All" not in selected_consignees:
        filtered_df = filtered_df.filter(pl.col("Consignee").is_in(selected_consignees))
    if "All" not in selected_months:
        filtered_df = filtered_df.filter(pl.col("Month").is_in(selected_months))
    
    st.write("### Filtered Data Preview:")
    st.write(filtered_df.head(10))
    
    # Logout Button
    if st.sidebar.button("Logout"):
        logout()
