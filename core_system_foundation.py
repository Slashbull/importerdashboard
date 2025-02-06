"""
core_system_foundation.py

Main entry point for the Import/Export Analytics Dashboard.
This module handles:
- User authentication and session management.
- Data ingestion (CSV and Google Sheets) with quality checks and preprocessing.
- Integration of smart filters.
- Navigation across various dashboards.
- Custom CSS and UI enhancements.
"""

import streamlit as st
import pandas as pd
import requests
from io import StringIO
import plotly.express as px
import logging
from datetime import datetime

# Import configuration and smart filters (aliased as apply_filters)
import config
from filters import smart_apply_filters as apply_filters

# Import dashboard modules
from market_overview import market_overview_dashboard
from competitor_intelligence_dashboard import competitor_intelligence_dashboard
from supplier_performance_dashboard import supplier_performance_dashboard
from state_level_market_insights import state_level_market_insights
from ai_based_alerts_forecasting import ai_based_alerts_forecasting
from reporting_data_exports import reporting_data_exports
from product_insights_dashboard import product_insights_dashboard

# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Fallback for Query Parameters Update
# -----------------------------------------------------------------------------
def update_query_params(params: dict):
    """
    Update URL query parameters using st.set_query_params,
    or fall back to st.experimental_set_query_params for older versions.
    """
    try:
        st.set_query_params(**params)
    except AttributeError:
        st.experimental_set_query_params(**params)

# -----------------------------------------------------------------------------
# Authentication & Session Management
# -----------------------------------------------------------------------------
def authenticate_user():
    """
    Display a login form and validate credentials from config.
    In production, consider a more robust authentication system.
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
                update_query_params({"tab": "Upload Data"})
                logger.info("User authenticated successfully.")
            else:
                st.sidebar.error("🚨 Invalid Username or Password")
                logger.warning("Failed login attempt for username: %s", username)
        st.stop()

def logout_button():
    """
    Display a logout button that clears the session and refreshes the app.
    """
    if st.sidebar.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# -----------------------------------------------------------------------------
# Data Ingestion & Preprocessing
# -----------------------------------------------------------------------------
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and convert numeric columns (currently only 'Tons') by removing commas and trimming spaces.
    Create a well-formatted 'Period' column using Month-Year and convert it to an ordered categorical type.
    """
    numeric_cols = ["Tons"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Create or convert 'Period' column
    if "Month" in df.columns and "Year" in df.columns:
        # Combine Month and Year into a string and then convert to datetime for proper ordering.
        def parse_period(row):
            try:
                return datetime.strptime(f"{row['Month']} {row['Year']}", "%b %Y")
            except Exception as e:
                logger.error("Error parsing Period for row %s: %s", row, e)
                return pd.NaT

        df["Period_dt"] = df.apply(parse_period, axis=1)
        # Also store a formatted string version
        df["Period"] = df["Period_dt"].dt.strftime("%b-%Y")
        # Optionally, convert Period into an ordered categorical type
        periods = df["Period_dt"].dropna().sort_values().unique()
        period_labels = [dt.strftime("%b-%Y") for dt in periods]
        df["Period"] = pd.Categorical(df["Period"], categories=period_labels, ordered=True)
    else:
        st.error("Missing 'Month' or 'Year' columns.")
    return df.convert_dtypes()

@st.cache_data(show_spinner=False)
def load_csv_data(uploaded_file) -> pd.DataFrame:
    """
    Load CSV data using pandas with caching to improve performance.
    """
    try:
        df = pd.read_csv(uploaded_file, low_memory=False)
    except Exception as e:
        st.error(f"🚨 Error processing CSV file: {e}")
        logger.error("Error in load_csv_data: %s", e)
        df = pd.DataFrame()
    return df

def upload_data():
    """
    Handle data upload from CSV or Google Sheets, preprocess it,
    perform quality checks, and store both the raw and filtered data in session state.
    """
    st.markdown("<h2 style='text-align: center;'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"), index=0)
    df = None

    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"],
                                         help="Upload your CSV file containing your data.")
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
                logger.error("Error loading Google Sheet: %s", e)

    if df is not None and not df.empty:
        df = preprocess_data(df)
        # Optionally, you can add more quality checks (e.g., duplicates, missing data) here.
        st.session_state["uploaded_data"] = df
        # Apply smart filters and store filtered data
        filtered_df, _ = apply_filters(df)
        st.session_state["filtered_data"] = filtered_df
        st.success("✅ Data loaded and filtered successfully!")
        logger.info("Data uploaded and preprocessed successfully.")
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
# Custom CSS and Header
# -----------------------------------------------------------------------------
def add_custom_css():
    custom_css = """
    <style>
        .main .block-container { padding: 1rem 2rem; }
        header { background-color: #1B4F72; padding: 10px; color: white; text-align: center; }
        h2 { color: #2E86C1; }
        h1 { color: #1B4F72; }
        .sidebar .sidebar-content { font-size: 14px; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def display_header():
    """
    Display a persistent header with the application title and current view.
    """
    current_tab = st.session_state.get("current_tab", "Upload Data")
    st.markdown(f"<header><h1>Import/Export Analytics Dashboard</h1><p>Current View: {current_tab}</p></header>", unsafe_allow_html=True)

def display_filter_summary():
    """
    Optionally, display a summary of currently active global filters.
    (This can be expanded based on what filters you use in your system.)
    """
    # Example: if you stored active filters in session_state, display them here.
    active_filters = st.session_state.get("active_filters", {})
    if active_filters:
        summary_text = "### Active Filters:\n"
        for key, value in active_filters.items():
            summary_text += f"- **{key}**: {', '.join(map(str, value))}\n"
        st.sidebar.markdown(summary_text)

# -----------------------------------------------------------------------------
# Main Application & Navigation
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Import/Export Analytics Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    add_custom_css()
    display_header()

    # Authenticate the user
    authenticate_user()
    logout_button()

    # Sidebar: Dashboard Navigation
    tabs = [
        "Upload Data", 
        "Market Overview", 
        "Competitor Intelligence", 
        "Supplier Performance", 
        "State-Level Market Insights", 
        "Product Insights",  
        "AI-Based Alerts & Forecasting", 
        "Reporting & Data Exports"
    ]
    current_tab = st.sidebar.selectbox("Go to:", tabs, index=tabs.index(st.session_state.get("current_tab", "Upload Data")))
    st.session_state["current_tab"] = current_tab

    # Optionally, display a summary of active filters
    # display_filter_summary()

    # If data exists, refresh filters before routing to dashboards
    if "uploaded_data" in st.session_state:
        try:
            filtered_df, _ = apply_filters(st.session_state["uploaded_data"])
            st.session_state["filtered_data"] = filtered_df
        except Exception as e:
            st.error(f"🚨 Error applying filters: {e}")
            logger.exception("Error in applying filters: %s", e)

    # Navigation Routing: Call the appropriate dashboard function based on selection.
    try:
        if current_tab == "Upload Data":
            df = upload_data()
            if "uploaded_data" in st.session_state:
                display_data_preview(st.session_state["uploaded_data"])
                # Provide a download button for the raw processed data.
                csv_data = st.session_state["uploaded_data"].to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download Processed Data", csv_data, "processed_data.csv", "text/csv")
        elif current_tab == "Market Overview":
            market_overview_dashboard(get_current_data())
        elif current_tab == "Competitor Intelligence":
            competitor_intelligence_dashboard(get_current_data())
        elif current_tab == "Supplier Performance":
            supplier_performance_dashboard(get_current_data())
        elif current_tab == "State-Level Market Insights":
            state_level_market_insights(get_current_data())
        elif current_tab == "Product Insights":
            product_insights_dashboard(get_current_data())
        elif current_tab == "AI-Based Alerts & Forecasting":
            ai_based_alerts_forecasting(get_current_data())
        elif current_tab == "Reporting & Data Exports":
            reporting_data_exports(get_current_data())
    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
        logger.exception("Error in main routing: %s", e)

if __name__ == "__main__":
    main()
