import streamlit as st
import pandas as pd
import requests
from io import StringIO
import plotly.express as px

# Import configuration and filters
import config
from filters import apply_filters

# Import dashboard modules
from market_overview import market_overview_dashboard
from competitor_intelligence_dashboard import competitor_intelligence_dashboard
from supplier_performance_dashboard import supplier_performance_dashboard
from state_level_market_insights import state_level_market_insights
from ai_based_alerts_forecasting import ai_based_alerts_forecasting
from reporting_data_exports import reporting_data_exports

# -----------------------------------------------------------------------------
# Authentication & Session Management
# -----------------------------------------------------------------------------
def authenticate_user():
    """
    Display a login form and validate credentials from config.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.sidebar.title("🔒 Login")
        username = st.sidebar.text_input("👤 Username", key="login_username")
        password = st.sidebar.text_input("🔑 Password", type="password", key="login_password")
        if st.sidebar.button("🚀 Login"):
            if username == config.USERNAME and password == config.PASSWORD:
                st.session_state["authenticated"] = True
                st.session_state["current_tab"] = "Upload Data"
                st.set_query_params(tab="Upload Data")
            else:
                st.sidebar.error("🚨 Invalid Username or Password")
        st.stop()

def logout_button():
    """Display a logout button that clears the session and refreshes the app."""
    if st.sidebar.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# -----------------------------------------------------------------------------
# Data Ingestion & Preprocessing
# -----------------------------------------------------------------------------
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and convert numeric columns by removing commas and trimming spaces.
    Now, only the 'Tons' column is used.
    """
    numeric_cols = ["Tons"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.convert_dtypes()

@st.cache_data(show_spinner=False)
def load_csv_data(uploaded_file) -> pd.DataFrame:
    """
    Load CSV data with caching.
    """
    try:
        df = pd.read_csv(uploaded_file, low_memory=False)
    except Exception as e:
        st.error(f"🚨 Error processing CSV file: {e}")
        df = pd.DataFrame()
    return df

def upload_data():
    """
    Handle data upload from CSV or Google Sheets, preprocess it,
    and store both the raw and filtered data in session_state.
    """
    st.markdown("<h2 style='text-align: center;'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"), index=0)
    df = None

    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"], help="Upload your CSV file containing your data.")
        if uploaded_file is not None:
            df = load_csv_data(uploaded_file)
    else:
        sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
        sheet_name = config.DEFAULT_SHEET_NAME
        if sheet_url and st.button("Load Google Sheet"):
            try:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                response = requests.get(csv_url)
                response.raise_for_status()
                df = pd.read_csv(StringIO(response.text), low_memory=False)
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")

    if df is not None and not df.empty:
        df = preprocess_data(df)
        st.session_state["uploaded_data"] = df
        # Immediately apply global filters
        filtered_df, _ = apply_filters(df)
        st.session_state["filtered_data"] = filtered_df
        st.success("✅ Data loaded and filtered successfully!")
    else:
        st.info("No data loaded yet. Please upload a file or provide a valid Google Sheet link.")
    return df

def display_data_preview(df: pd.DataFrame):
    """
    Display the first 50 rows and summary statistics of the data.
    """
    st.markdown("### 🔍 Data Preview (First 50 Rows)")
    st.dataframe(df.head(50))
    st.markdown("### 📊 Data Summary")
    st.write(df.describe(include="all"))

def get_current_data():
    """
    Return the filtered data if available; otherwise, return the raw uploaded data.
    """
    return st.session_state.get("filtered_data", st.session_state.get("uploaded_data"))

# -----------------------------------------------------------------------------
# Custom CSS for a Polished Look
# -----------------------------------------------------------------------------
def add_custom_css():
    custom_css = """
    <style>
        .main .block-container {
            padding: 1rem 2rem;
        }
        h2 { color: #2E86C1; }
        h1 { color: #1B4F72; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Main Application & Navigation
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Import/Export Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")
    add_custom_css()

    # Authenticate the user
    authenticate_user()
    logout_button()

    # Sidebar navigation tabs
    tabs = [
        "Upload Data", 
        "Market Overview", 
        "Competitor Intelligence", 
        "Supplier Performance", 
        "State-Level Market Insights", 
        "AI-Based Alerts & Forecasting", 
        "Reporting & Data Exports"
    ]
    current_tab = st.sidebar.radio("Go to:", tabs, index=tabs.index(st.session_state.get("current_tab", "Upload Data")))
    st.session_state["current_tab"] = current_tab

    # If data exists, show the global filter panel
    if "uploaded_data" in st.session_state:
        filtered_df, _ = apply_filters(st.session_state["uploaded_data"])
        st.session_state["filtered_data"] = filtered_df

    # Route to the selected dashboard page
    if current_tab == "Upload Data":
        df = upload_data()
        if "uploaded_data" in st.session_state:
            display_data_preview(st.session_state["uploaded_data"])
            csv_data = st.session_state["uploaded_data"].to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Processed Data", data=csv_data, file_name="processed_data.csv", mime="text/csv")
    elif current_tab == "Market Overview":
        try:
            market_overview_dashboard(get_current_data())
        except Exception as e:
            st.error(f"🚨 Error loading Market Overview Dashboard: {e}")
    elif current_tab == "Competitor Intelligence":
        try:
            competitor_intelligence_dashboard(get_current_data())
        except Exception as e:
            st.error(f"🚨 Error loading Competitor Intelligence Dashboard: {e}")
    elif current_tab == "Supplier Performance":
        try:
            supplier_performance_dashboard(get_current_data())
        except Exception as e:
            st.error(f"🚨 Error loading Supplier Performance Dashboard: {e}")
    elif current_tab == "State-Level Market Insights":
        try:
            state_level_market_insights(get_current_data())
        except Exception as e:
            st.error(f"🚨 Error loading State-Level Market Insights Dashboard: {e}")
    elif current_tab == "AI-Based Alerts & Forecasting":
        try:
            ai_based_alerts_forecasting(get_current_data())
        except Exception as e:
            st.error(f"🚨 Error loading AI-Based Alerts & Forecasting Dashboard: {e}")
    elif current_tab == "Reporting & Data Exports":
        try:
            reporting_data_exports(get_current_data())
        except Exception as e:
            st.error(f"🚨 Error loading Reporting & Data Exports Dashboard: {e}")

if __name__ == "__main__":
    main()
