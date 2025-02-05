import streamlit as st
import pandas as pd
from io import StringIO

# ---- Secure User Authentication ---- #
USERS = {"admin": "admin123"}  # Simple Username & Password

# ---- Session State Management ---- #
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

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
    st.markdown("Ensure your file is in CSV format for optimal performance.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], help="Supported file format: .csv")
    if uploaded_file is not None:
        try:
            # Remove previously uploaded file
            st.session_state["uploaded_file"] = None
            
            # Read and cache the new file
            file_bytes = uploaded_file.getvalue()
            st.session_state["uploaded_file"] = file_bytes
            st.success("File uploaded successfully! Processing data...")
            st.button("Proceed to Dashboard", on_click=lambda: st.experimental_rerun())
        except Exception as e:
            st.error(f"Error processing file: {e}")

# ---- Data Processing Function ---- #
def process_data():
    if st.session_state["uploaded_file"]:
        df = pd.read_csv(StringIO(st.session_state["uploaded_file"].decode("utf-8")))
        
        # Convert 'Quanity (Kgs)' to numeric
        df["Quanity (Kgs)"] = df["Quanity (Kgs)"].str.replace(" Kgs", "", regex=False).astype(float)
        df["Quanity (Tons)"] = df["Quanity (Tons)"].str.replace(" tons", "", regex=False).astype(float)
        
        # Convert Month to Numeric
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                     "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        df["Month"] = df["Month"].map(month_map)
        
        # Handle missing values
        df.fillna("N/A", inplace=True)
        
        return df
    return None

# ---- Dashboard Page ---- #
def dashboard():
    st.title("📊 Importer Decision-Making Dashboard")
    st.sidebar.button("Logout", on_click=logout)
    
    df = process_data()
    if df is not None:
        st.write("### Processed Data Overview")
        st.dataframe(df.head())
        
        # Key Insights
        st.subheader("Key Metrics")
        total_imports = df["Quanity (Kgs)"].sum()
        unique_exporters = df["Exporter"].nunique()
        unique_consignees = df["Consignee"].nunique()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Import Volume (Kgs)", f"{total_imports:,.2f}")
        col2.metric("Unique Exporters", unique_exporters)
        col3.metric("Unique Consignees", unique_consignees)
    else:
        st.warning("No file uploaded. Please upload a CSV file first.")

# ---- Main Application Logic ---- #
if not st.session_state["authenticated"]:
    login()
elif not st.session_state["uploaded_file"]:
    file_upload()
else:
    dashboard()

# Save file as core_system_foundation.py
