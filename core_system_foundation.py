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
    """Update URL query parameters using st.query_params.update()."""
    try:
        st.query_params.update(**params)
    except Exception as e:
        logger.error("Error updating query parameters: %s", e)

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
        st.rerun()

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
    Data is persisted for the duration of the session.
    On the Home page, filters are not displayed.
    """
    st.markdown("<h2 style='text-align: center;'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    # Check if data is already uploaded.
    if "uploaded_data" in st.session_state:
        st.info("Data is already loaded. Use 'Reset Data' (or 'Reset Filters') to clear current settings.")
        return st.session_state["uploaded_data"]
    
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
        # On non-Home pages, filters will be displayed.
        st.sidebar.header("Filters")
        filtered_df, _ = apply_filters(df)
        st.session_state["filtered_data"] = filtered_df
        st.success("✅ Data loaded and filtered successfully!")
        logger.info("Data uploaded and preprocessed successfully.")
    else:
        st.info("No data loaded yet. Please upload a file or provide a valid Google Sheet link.")
    return df

def reset_filters():
    """
    Reset all filter selections by clearing the keys used by the multiselect widgets.
    This forces the filters to return to their default state.
    """
    keys_to_reset = ["multiselect_Year", "multiselect_Month", "multiselect_Consignee State",
                     "multiselect_Consignee", "multiselect_Exporter", "multiselect_Product"]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def get_current_data():
    """
    Return filtered data if available; otherwise, return raw uploaded data.
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

def main():
    st.set_page_config(page_title="Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")
    
    # Sidebar navigation using radio buttons.
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

    # Add Reset Data and Reset Filters buttons.
    if "uploaded_data" in st.session_state:
        st.sidebar.markdown("**Data Status:**")
        st.sidebar.success("Data is already loaded.")
        if st.sidebar.button("Reset Data", key="reset_data"):
            st.session_state.pop("uploaded_data", None)
            st.session_state.pop("filtered_data", None)
            st.rerun()
        if st.sidebar.button("Reset Filters", key="reset_filters"):
            reset_filters()

    # Permanently display filters in the sidebar on non‑Home pages.
    if selected_page != "Home" and "uploaded_data" in st.session_state:
        st.sidebar.header("Filters")
        filtered_df, _ = apply_filters(st.session_state["uploaded_data"])
        st.session_state["filtered_data"] = filtered_df

    authenticate_user()
    logout_button()
    
    if selected_page == "Home":
        st.markdown('<div>', unsafe_allow_html=True)
        st.header("Executive Summary & Data Upload")
        df = upload_data()
        if df is not None and not df.empty:
            # On the Home page, do not display data preview.
            st.sidebar.download_button("📥 Download Processed Data", df.to_csv(index=False).encode("utf-8"), "processed_data.csv", "text/csv")
        else:
            st.info("Please upload your data to view insights.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        data = get_current_data()
        if data is None or data.empty:
            st.error("No data loaded. Please upload your data on the Home page first.")
        else:
            st.markdown('<div>', unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)
    
    display_footer()

if __name__ == "__main__":
    main()
