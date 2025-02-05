import streamlit as st
import polars as pl
import time
from io import StringIO
from market_overview_dashboard import market_dashboard

# ---- Secure User Authentication ---- #
USERS = {"admin": "admin123"}  # Simple Username & Password

# ---- Session State Management ---- #
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "session_start_time" not in st.session_state:
    st.session_state["session_start_time"] = time.time()
if "current_screen" not in st.session_state:
    st.session_state["current_screen"] = "Market Overview"

# Auto logout after 30 min of inactivity with warning
remaining_time = 1800 - (time.time() - st.session_state["session_start_time"])
if remaining_time <= 0:
    st.session_state["authenticated"] = False
    st.experimental_rerun()
st.sidebar.warning(f"⚠️ Auto logout in {int(remaining_time // 60)} min {int(remaining_time % 60)} sec")

# ---- Navigation Menu ---- #
def navigation_menu():
    st.sidebar.header("Navigation")
    selected_screen = st.sidebar.selectbox("Choose Dashboard", ["Market Overview", "Competitor Insights", "Processed Data Download"])
    st.session_state["current_screen"] = selected_screen

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

# ---- Data Validation Function ---- #
def validate_data(file):
    required_columns = ["SR NO.", "Job No.", "Consignee", "Exporter", "Quanity (Kgs)", "Quanity (Tons)", "Month", "Year", "Consignee State"]
    try:
        df = pl.read_csv(StringIO(file.decode("utf-8")))
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing Required Columns: {missing_columns}")
            return False
        return True
    except Exception as e:
        st.error(f"Error validating file: {e}")
        return False

# ---- File Upload Page ---- #
def file_upload():
    st.title("📂 Upload Your Import Data")
    st.markdown("Only CSV files are supported.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], help="Upload your CSV file")
    if uploaded_file is not None:
        if validate_data(uploaded_file.getvalue()):
            try:
                st.session_state["uploaded_file"] = uploaded_file.getvalue()
                st.success("File uploaded successfully! Redirecting to Market Overview...")
                st.session_state["current_screen"] = "Market Overview"
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error processing file: {e}")

# ---- Processed Data Download Page ---- #
def processed_data_download():
    st.title("📥 Processed Data Download")
    if st.session_state["uploaded_file"] is not None:
        st.download_button("Download Uploaded CSV", st.session_state["uploaded_file"], "uploaded_data.csv", "text/csv")
    else:
        st.warning("No data uploaded. Please upload a file first.")

# ---- Competitor Insights Placeholder ---- #
def competitor_insights():
    st.title("Competitor Insights")
    st.markdown("This section is under development. Advanced insights will be available soon.")

# ---- Main Application Logic ---- #
if not st.session_state["authenticated"]:
    login()
else:
    navigation_menu()
    st.sidebar.button("Logout", on_click=logout)

    if st.session_state["current_screen"] == "Market Overview":
        if st.session_state["uploaded_file"] is not None:
            market_dashboard(st.session_state["uploaded_file"])
        else:
            file_upload()
    elif st.session_state["current_screen"] == "Competitor Insights":
        competitor_insights()
    elif st.session_state["current_screen"] == "Processed Data Download":
        processed_data_download()

# Save file as core_system_foundation.py
