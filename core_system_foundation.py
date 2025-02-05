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

def load_data(file):
    """Load CSV or Excel data into a Polars DataFrame."""
    if file.name.endswith(".csv"):
        df = pl.read_csv(file)
    else:
        df = pl.read_excel(file)
    return df

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Raw Data Preview:")
    st.write(df.head(10))
    
    # ==================== DATA CLEANING & PROCESSING ====================
    
    # Convert Quantity column to numeric (Kgs & Tons Toggle)
    df = df.with_columns(
        pl.col("Quanity").str.replace_all("[^0-9]", "").cast(pl.Float64).alias("Quantity_Kgs")
    )
    df = df.with_columns(
        (pl.col("Quantity_Kgs") / 1000).alias("Quantity_Tons")
    )
    
    # Convert Month column to numeric format
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    df = df.with_columns(
        pl.col("Month").replace(month_map).alias("Month_Num")
    )
    
    # Display cleaned data
    st.write("### Processed Data Preview:")
    st.write(df.head(10))
    
    # ==================== FILTER SYSTEM ====================
    st.sidebar.subheader("Filters")
    selected_year = st.sidebar.selectbox("Select Year", df["Year"].unique().to_list())
    selected_state = st.sidebar.selectbox("Select Consignee State", ["All"] + df["Consignee State"].unique().to_list())
    selected_supplier = st.sidebar.selectbox("Select Exporter", ["All"] + df["Exporter"].unique().to_list())
    
    # Apply filters
    filtered_df = df.filter(pl.col("Year") == selected_year)
    if selected_state != "All":
        filtered_df = filtered_df.filter(pl.col("Consignee State") == selected_state)
    if selected_supplier != "All":
        filtered_df = filtered_df.filter(pl.col("Exporter") == selected_supplier)
    
    st.write("### Filtered Data Preview:")
    st.write(filtered_df.head(10))
    
    # Logout Button
    if st.sidebar.button("Logout"):
        logout()
