import streamlit as st
import pandas as pd
import requests
from io import StringIO
import plotly.express as px
import logging
from datetime import datetime

# -----------------------------------------------------------------------------
# Import configuration, smart filters, and dashboard modules
# -----------------------------------------------------------------------------
import config
from filters import smart_apply_filters as apply_filters

from market_overview_dashboard import market_overview_dashboard
from competitor_intelligence_dashboard import competitor_intelligence_dashboard
from supplier_performance_dashboard import supplier_performance_dashboard
from state_level_market_insights import state_level_market_insights
from ai_based_alerts_forecasting import ai_based_alerts_forecasting
from reporting_data_exports import reporting_data_exports, overall_dashboard_report
from product_insights_dashboard import product_insights_dashboard

# -----------------------------------------------------------------------------
# Set Streamlit page configuration (must be first!)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------
def update_query_params(params: dict):
    """
    Update URL query parameters using the experimental API.
    Merges current query parameters with the provided ones.
    """
    try:
        current_params = st.experimental_get_query_params()
        current_params.update(params)
        st.experimental_set_query_params(**current_params)
    except Exception as e:
        logger.error("Error updating query parameters: %s", e)

def authenticate_user():
    """
    Display a login form and validate credentials.
    Uses session_state to remember if the user is already authenticated.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.sidebar:
            st.title("🔒 Login")
            username = st.text_input("👤 Username", key="login_username")
            password = st.text_input("🔑 Password", type="password", key="login_password")
            if st.button("🚀 Login", key="login_button"):
                if username == config.USERNAME and password == config.PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.page = "Home"
                    update_query_params({"page": "Home"})
                    logger.info("User authenticated successfully.")
                else:
                    st.error("🚨 Invalid Username or Password")
                    logger.warning("Failed login attempt for username: %s", username)
        if not st.session_state.authenticated:
            st.stop()

def logout_button():
    """Display a logout button that clears the session state and reruns the app."""
    if st.sidebar.button("🔓 Logout", key="logout_button"):
        st.session_state.clear()
        st.rerun()

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataset:
      - Convert 'Tons' to numeric (remove commas and trim spaces).
      - Create a datetime column ('Period_dt') from Month and Year.
      - Generate an ordered categorical 'Period' (format "Mon-Year") for time‑series analysis.
    """
    if "Tons" in df.columns:
        df["Tons"] = df["Tons"].astype(str).str.replace(",", "", regex=False).str.strip()
        df["Tons"] = pd.to_numeric(df["Tons"], errors="coerce")
    if "Month" in df.columns and "Year" in df.columns:
        try:
            df["Period_dt"] = df.apply(lambda row: datetime.strptime(f"{row['Month']} {row['Year']}", "%b %Y"), axis=1)
            df["Period"] = df["Period_dt"].dt.strftime("%b-%Y")
            sorted_periods = sorted(df["Period_dt"].dropna().unique())
            period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
            df["Period"] = pd.Categorical(df["Period"], categories=period_labels, ordered=True)
        except Exception as e:
            st.error("Error parsing 'Month' and 'Year'. Ensure they are in abbreviated format (e.g., Jan) and Year is numeric.")
            logger.error("Error parsing Period: %s", e)
    else:
        st.error("Missing 'Month' or 'Year' columns.")
    return df.convert_dtypes()

@st.cache_data(show_spinner=False)
def load_csv_data(uploaded_file) -> pd.DataFrame:
    """Load CSV data with caching and remove extraneous unnamed columns."""
    try:
        df = pd.read_csv(uploaded_file, low_memory=False)
        # Remove any columns that start with "Unnamed"
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    except Exception as e:
        st.error(f"🚨 Error processing CSV file: {e}")
        logger.error("Error in load_csv_data: %s", e)
        return pd.DataFrame()

def upload_data():
    """
    Handle data ingestion:
      - Auto-load from a configured Google Sheet if available.
      - Otherwise, let the user choose between uploading a CSV or providing a Google Sheet link.
      - Preprocess and cache the data in session_state.
    """
    st.markdown("<h2 style='text-align: center;'>📂 Data Ingestion</h2>", unsafe_allow_html=True)
    
    if "uploaded_data" in st.session_state:
        st.info("Data is already loaded. Use 'Reset Data' or 'Reset Filters' to clear current settings.")
        return st.session_state.uploaded_data

    df = None
    # Auto-load from configured Google Sheet if provided.
    if config.GOOGLE_SHEET_LINK:
        st.info("Loading data from the configured Google Sheet...")
        sheet_url = config.GOOGLE_SHEET_LINK
        sheet_name = config.DEFAULT_SHEET_NAME
        try:
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            response = requests.get(csv_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text), low_memory=False)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            st.success("✅ Google Sheet loaded successfully from configuration.")
        except Exception as e:
            st.error(f"🚨 Error loading Google Sheet from config: {e}")
            logger.error("Error loading Google Sheet from config: %s", e)
    
    # If no auto-loaded data, allow the user to choose a source.
    if df is None:
        upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"), index=0, key="data_source_option")
        if upload_option == "Upload CSV":
            uploaded_file = st.file_uploader(
                "Upload CSV File", 
                type=["csv"],
                help="Upload your CSV file containing your data.",
                key="csv_uploader"
            )
            if uploaded_file is not None:
                df = load_csv_data(uploaded_file)
        else:
            sheet_url = st.text_input("🔗 Enter Google Sheet Link:", key="gsheet_link")
            sheet_name = config.DEFAULT_SHEET_NAME
            if sheet_url and st.button("Load Google Sheet", key="load_gsheet"):
                try:
                    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                    response = requests.get(csv_url)
                    response.raise_for_status()
                    df = pd.read_csv(StringIO(response.text), low_memory=False)
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                except Exception as e:
                    st.error(f"🚨 Error loading Google Sheet: {e}")
                    logger.error("Error loading Google Sheet: %s", e)
    
    if df is not None and not df.empty:
        df = preprocess_data(df)
        st.session_state.uploaded_data = df
        st.sidebar.header("Filters")
        filtered_df, _ = apply_filters(df)
        st.session_state.filtered_data = filtered_df
        st.success("✅ Data loaded and filtered successfully!")
    else:
        st.info("No data loaded yet. Please upload a file or provide a valid Google Sheet link.")
    return df

def reset_filters():
    """
    Reset all filter selections by clearing the keys for filter widgets,
    then rerun the app to update the filtered data.
    """
    filter_keys = [
        "multiselect_Year", "multiselect_Month", "multiselect_Consignee State",
        "multiselect_Consignee", "multiselect_Exporter", "multiselect_Product"
    ]
    for key in filter_keys:
        st.session_state[key] = []
    st.rerun()

def get_current_data():
    """
    Return the filtered data if available; otherwise, return the raw uploaded data.
    """
    return st.session_state.get("filtered_data", st.session_state.get("uploaded_data"))

def display_footer():
    """Display a simple footer."""
    footer_html = """
    <div style="text-align: center; padding: 10px; color: #666;">
        © 2025 Your Company. All rights reserved.
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Main Application
# -----------------------------------------------------------------------------
def main():
    with st.sidebar:
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
        selected_page = st.radio("Navigation", nav_options, index=0, key="nav_radio")
        st.session_state.page = selected_page

        # Logout and data reset buttons
        logout_button()
        if "uploaded_data" in st.session_state:
            st.markdown("**Data Status:**")
            st.success("Data is loaded.")
            if st.button("Reset Data", key="reset_data"):
                st.session_state.pop("uploaded_data", None)
                st.session_state.pop("filtered_data", None)
                st.rerun()
            if st.button("Reset Filters", key="reset_filters"):
                for key in ["multiselect_Year", "multiselect_Month", "multiselect_Consignee State",
                            "multiselect_Consignee", "multiselect_Exporter", "multiselect_Product"]:
                    st.session_state[key] = []
                st.rerun()

    # Ensure the user is authenticated
    authenticate_user()

    # Render the page content based on navigation selection
    if selected_page == "Home":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header("Executive Summary & Data Upload")
        df = upload_data()
        if df is not None and not df.empty:
            st.sidebar.download_button(
                "📥 Download Processed Data",
                df.to_csv(index=False).encode("utf-8"),
                "processed_data.csv",
                "text/csv",
                key="download_button"
            )
            st.subheader("Data Preview:")
            st.dataframe(df.head(10))
        else:
            st.info("Please upload your data to view insights.")
        st.markdown('</div>', unsafe_allow_html=True)
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
                report_option = st.radio(
                    "Choose Reporting Option:",
                    ("Interactive Overall Report", "Export Report"),
                    key="report_option"
                )
                if report_option == "Interactive Overall Report":
                    overall_dashboard_report(data)
                else:
                    reporting_data_exports(data)
            st.markdown('</div>', unsafe_allow_html=True)

    display_footer()

# -----------------------------------------------------------------------------
# Run the Application
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
