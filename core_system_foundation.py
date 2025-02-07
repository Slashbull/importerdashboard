import streamlit as st
import pandas as pd
import requests
from io import StringIO
import plotly.express as px
import logging
from datetime import datetime

# Import configuration and smart filters
import config
from filters import smart_apply_filters as apply_filters

# Import dashboard modules
from market_overview_dashboard import market_overview_dashboard
from competitor_intelligence_dashboard import competitor_intelligence_dashboard
from supplier_performance_dashboard import supplier_performance_dashboard
from state_level_market_insights import state_level_market_insights
from ai_based_alerts_forecasting import ai_based_alerts_forecasting
from reporting_data_exports import reporting_data_exports
from product_insights_dashboard import product_insights_dashboard

# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def update_query_params(params: dict):
    """Update URL query parameters using st.set_query_params."""
    st.set_query_params(**params)

def authenticate_user():
    """Display a login form and validate credentials."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.sidebar.title("🔒 Login")
        username = st.sidebar.text_input("👤 Username", key="login_username")
        password = st.sidebar.text_input("🔑 Password", type="password", key="login_password")
        if st.sidebar.button("🚀 Login"):
            if username == config.USERNAME and password == config.PASSWORD:
                st.session_state["authenticated"] = True
                st.session_state["page"] = "Home"
                update_query_params({"page": "Home"})
                logger.info("User authenticated successfully.")
            else:
                st.sidebar.error("🚨 Invalid Username or Password")
                logger.warning("Failed login attempt for username: %s", username)
        st.stop()

def logout_button():
    """Display a logout button that clears the session and refreshes the app."""
    if st.sidebar.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataset:
      - Convert 'Tons' to numeric.
      - Create a datetime column ('Period_dt') from Month and Year.
      - Create an ordered categorical 'Period' for time-series analysis.
    """
    for col in ["Tons"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Month" in df.columns and "Year" in df.columns:
        try:
            df["Period_dt"] = df.apply(lambda row: datetime.strptime(f"{row['Month']} {row['Year']}", "%b %Y"), axis=1)
        except Exception as e:
            st.error("Error parsing 'Month' and 'Year'. Ensure they are in 'Mon' format and numeric.")
            logger.error("Error parsing Period: %s", e)
            return df
        df["Period"] = df["Period_dt"].dt.strftime("%b-%Y")
        sorted_periods = sorted(df["Period_dt"].dropna().unique())
        period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
        df["Period"] = pd.Categorical(df["Period"], categories=period_labels, ordered=True)
    else:
        st.error("Missing 'Month' or 'Year' columns.")
    return df.convert_dtypes()

@st.cache_data(show_spinner=False)
def load_csv_data(uploaded_file) -> pd.DataFrame:
    """Load CSV data with caching."""
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
    and store both raw and filtered data in session state.
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
        st.session_state["uploaded_data"] = df
        # Permanently display filters in the sidebar:
        st.sidebar.header("Filters")
        filtered_df, _ = apply_filters(df)
        st.session_state["filtered_data"] = filtered_df
        st.success("✅ Data loaded and filtered successfully!")
        logger.info("Data uploaded and preprocessed successfully.")
    else:
        st.info("No data loaded yet. Please upload a file or provide a valid Google Sheet link.")
    return df

def display_data_preview(df: pd.DataFrame):
    """Display a preview (first 50 rows) and summary statistics of the data."""
    st.markdown("### 🔍 Data Preview (First 50 Rows)")
    st.dataframe(df.head(50))
    st.markdown("### 📊 Data Summary")
    st.write(df.describe(include="all"))

def get_current_data():
    """Return filtered data if available; otherwise, return raw uploaded data."""
    return st.session_state.get("filtered_data", st.session_state.get("uploaded_data"))

def add_custom_css():
    custom_css = """
    <style>
        /* Fixed header styling */
        .fixed-header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #1B4F72;
            color: white;
            padding: 10px 20px;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .fixed-header h1 {
            margin: 0;
            font-size: 1.8em;
        }
        /* Main content margin to avoid overlap with header */
        .main-content {
            margin-top: 70px;
        }
        /* Sidebar styling */
        .sidebar .sidebar-content { font-size: 14px; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def display_header():
    """Display a fixed header with the dashboard title and current page."""
    current_page = st.session_state.get("page", "Home")
    header_html = f"""
    <div class="fixed-header">
        <h1>Import/Export Analytics Dashboard</h1>
        <span style="font-size:1.2em;">Current Page: {current_page}</span>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def display_footer():
    """Display a simple footer."""
    footer_html = """
    <div style="text-align: center; padding: 10px; color: #666;">
        © 2025 Your Company. All rights reserved.
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Import/Export Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")
    add_custom_css()
    display_header()
    
    # Use sidebar radio for main navigation.
    nav_options = [
        "Home",
        "Market Overview",
        "Competitor Intelligence",
        "Supplier Performance",
        "State-Level Insights",
        "Product Insights",
        "Alerts & Forecasting",
        "Reporting"
    ]
    selected_page = st.sidebar.radio("Navigation", nav_options, index=0)
    st.session_state["page"] = selected_page
    
    # Permanently display filters in the sidebar if data is loaded.
    if "uploaded_data" in st.session_state:
        st.sidebar.header("Filters")
        filtered_df, _ = apply_filters(st.session_state["uploaded_data"])
        st.session_state["filtered_data"] = filtered_df
    
    authenticate_user()
    logout_button()
    
    if selected_page == "Home":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header("Executive Summary & Data Upload")
        df = upload_data()
        if df is not None and not df.empty:
            display_data_preview(df)
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Processed Data", csv_data, "processed_data.csv", "text/csv")
        else:
            st.info("Please upload your data to view insights.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        data = get_current_data()
        if data is None or data.empty:
            st.error("No data loaded. Please upload your data on the Home page first.")
        else:
            st.markdown('<div class="main-content">', unsafe_allow_html=True)
            if selected_page == "Market Overview":
                market_overview_dashboard(data)
            elif selected_page == "Competitor Intelligence":
                competitor_intelligence_dashboard(data)
            elif selected_page == "Supplier Performance":
                supplier_performance_dashboard(data)
            elif selected_page == "State-Level Insights":
                state_level_market_insights(data)
            elif selected_page == "Product Insights":
                product_insights_dashboard(data)
            elif selected_page == "Alerts & Forecasting":
                ai_based_alerts_forecasting(data)
            elif selected_page == "Reporting":
                reporting_data_exports(data)
            st.markdown("</div>", unsafe_allow_html=True)
    
    display_footer()

if __name__ == "__main__":
    main()
