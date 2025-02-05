import streamlit as st
import polars as pl
import time
from io import StringIO

# ---- Secure User Authentication ---- #
USERS = {"admin": "admin123"}  # Simple Username & Password

# ---- Session State Management ---- #
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "session_start_time" not in st.session_state:
    st.session_state["session_start_time"] = time.time()

# Auto logout after 30 min of inactivity with warning
remaining_time = 1800 - (time.time() - st.session_state["session_start_time"])
if remaining_time <= 0:
    st.session_state["authenticated"] = False
    st.experimental_rerun()
st.sidebar.warning(f"⚠️ Auto logout in {int(remaining_time // 60)} min {int(remaining_time % 60)} sec")

# ---- Login Page ---- #
def login():
    st.title("🔒 Secure Login")
    st.subheader("Welcome to the Importer Dashboard")
    st.markdown("Please enter your credentials to access the system.")
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login", use_container_width=True):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["session_start_time"] = time.time()
            st.experimental_rerun()
        else:
            st.error("Invalid Username or Password")

# ---- Logout Function ---- #
def logout():
    st.session_state["authenticated"] = False
    st.session_state["uploaded_file"] = None
    st.experimental_rerun()

# ---- File Upload Page ---- #
def file_upload():
    st.title("📂 Upload Your Import Data")
    st.markdown("Only CSV files are supported.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], help="Upload your CSV file")
    if uploaded_file is not None:
        try:
            st.session_state["uploaded_file"] = uploaded_file.getvalue()
            st.success("File uploaded successfully! Processing data...")
            st.button("Proceed to Dashboard", on_click=lambda: st.experimental_rerun())
        except Exception as e:
            st.error(f"Error processing file: {e}")

# ---- Data Schema Validation ---- #
def validate_schema(df):
    required_columns = {"SR NO.": pl.Int64, "Job No.": pl.Int64, "Consignee": pl.Utf8, "Exporter": pl.Utf8, "Quanity (Kgs)": pl.Utf8,
                        "Quanity (Tons)": pl.Utf8, "Month": pl.Utf8, "Year": pl.Int64, "Consignee State": pl.Utf8}
    for col, dtype in required_columns.items():
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return False
        if df[col].dtype != dtype:
            st.error(f"Column {col} has incorrect data type. Expected {dtype}, found {df[col].dtype}")
            return False
    return True

# ---- Data Processing Function ---- #
@st.cache_data(max_entries=10)
def process_data(file):
    df = pl.read_csv(StringIO(file.decode("utf-8")))
    
    if not validate_schema(df):
        return None
    
    # Convert 'Quanity (Kgs)' and 'Quanity (Tons)' to numeric
    df = df.with_columns([
        pl.col("Quanity (Kgs)").str.replace(" Kgs", "").cast(pl.Float64),
        pl.col("Quanity (Tons)").str.replace(" tons", "").cast(pl.Float64)
    ])
    
    # Convert Month to Numeric
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                 "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    df = df.with_columns(pl.col("Month").replace(month_map))
    
    df = df.fill_null("N/A")
    return df

# ---- Dashboard Page ---- #
def dashboard():
    st.title("📊 Importer Decision-Making Dashboard")
    st.sidebar.button("Logout", on_click=logout)
    
    df = process_data(st.session_state["uploaded_file"])
    if df is not None:
        st.write("### Processed Data Overview")
        st.dataframe(df.head())
        
        st.subheader("Key Metrics")
        total_imports = df["Quanity (Kgs)"].sum()
        unique_exporters = df["Exporter"].nunique()
        unique_consignees = df["Consignee"].nunique()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Import Volume (Kgs)", f"{total_imports:,.2f}")
        col2.metric("Unique Exporters", unique_exporters)
        col3.metric("Unique Consignees", unique_consignees)
        
        st.subheader("🏆 Top 5 Consignees by Import Volume")
        top_consignees = df.groupby("Consignee")["Quanity (Kgs)"].sum().top_k(5)
        st.dataframe(top_consignees)
        
        st.subheader("🚢 Top 5 Exporters by Import Volume")
        top_exporters = df.groupby("Exporter")["Quanity (Kgs)"].sum().top_k(5)
        st.dataframe(top_exporters)

        # Add Download Button
        csv_data = df.write_csv()
        st.download_button("📥 Download Processed Data", csv_data, "processed_data.csv", "text/csv")
    else:
        st.warning("No file uploaded or invalid schema. Please upload a valid CSV file.")

# ---- Main Application Logic ---- #
if not st.session_state["authenticated"]:
    login()
elif not st.session_state["uploaded_file"]:
    file_upload()
else:
    dashboard()

# Save file as core_system_foundation.py
