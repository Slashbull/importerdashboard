import streamlit as st
import pandas as pd
import requests
from io import StringIO
from market_overview import market_overview_dashboard
from competitor_intelligence_dashboard import competitor_intelligence_dashboard
from supplier_performance_dashboard import supplier_performance_dashboard
from state_level_market_insights import state_level_market_insights
from ai_based_alerts_forecasting import ai_based_alerts_forecasting

# ---- Core System Foundation (Future-Ready Design) ---- #

# Sidebar Navigation with Secure Login
st.sidebar.title("📌 Navigation")
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    username = st.sidebar.text_input("👤 Username", key="login_username")
    password = st.sidebar.text_input("🔑 Password", type="password", key="login_password")
    if st.sidebar.button("🚀 Login"):
        if username == "admin" and password == "admin123":
            st.session_state["authenticated"] = True
            st.session_state["current_tab"] = "Upload Data"
            st.query_params(tab="Upload Data")
        else:
            st.sidebar.error("🚨 Invalid Username or Password")
    st.stop()

st.sidebar.success("✅ Logged in")
st.sidebar.button("🔓 Logout", on_click=lambda: st.session_state.update({"authenticated": False, "uploaded_data": None}))

# Navigation
tab_selection = st.sidebar.radio("Go to:", ["Upload Data", "Market Overview", "Competitor Intelligence", "Supplier Performance", "State-Level Market Insights", "AI-Based Alerts & Forecasting"])

if tab_selection == "Upload Data":
    # ---- Upload Data Page ---- #
    st.markdown("<h2 class='centered'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"))
    df = None

    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"], help="Upload a CSV file containing import data.")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, low_memory=False)
                st.session_state["uploaded_data"] = df
                st.success("✅ File uploaded successfully!")
            except Exception as e:
                st.error(f"🚨 Error processing the CSV file: {e}")

    elif upload_option == "Google Sheet Link":
        sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
        sheet_name = "data"  # Fixed sheet name selection
        if sheet_url and st.button("Load Google Sheet"):
            try:
                # Extract Google Sheet ID from URL
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                
                # Fetch data from Google Sheets Viewer Mode
                response = requests.get(csv_url)
                response.raise_for_status()
                df = pd.read_csv(StringIO(response.text), low_memory=False)
                
                # Validate data
                if df.empty:
                    st.error("🚨 The sheet is empty or the sheet name is incorrect.")
                else:
                    st.session_state["uploaded_data"] = df
                    st.success(f"✅ Data loaded successfully from sheet: {sheet_name}")
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")

    # ---- Data Handling for Large Datasets ---- #
    if "uploaded_data" in st.session_state:
        st.markdown("### 🔍 Data Preview (First 50 Rows)")
        try:
            st.dataframe(st.session_state["uploaded_data"].head(50))  # Displaying only the first 50 rows for performance
        except Exception as e:
            st.error(f"🚨 Error displaying data preview: {e}")
        
        st.markdown("### 📊 Data Summary")
        try:
            st.write(st.session_state["uploaded_data"].describe())
        except Exception as e:
            st.error(f"🚨 Error generating data summary: {e}")
        
        # Optimize storage for large datasets
        try:
            st.session_state["uploaded_data"] = st.session_state["uploaded_data"].convert_dtypes()
        except Exception as e:
            st.error(f"🚨 Error optimizing data types: {e}")
        
        csv = st.session_state["uploaded_data"].to_csv(index=False).encode('utf-8')
        
        if "csv_downloaded" not in st.session_state:
            st.session_state["csv_downloaded"] = False
        
        if not st.session_state["csv_downloaded"]:
            try:
                if st.download_button("📥 Download Processed Data", csv, "processed_data.csv", "text/csv"):
                    st.session_state["csv_downloaded"] = True
            except Exception as e:
                st.error(f"🚨 Error with download button: {e}")
elif tab_selection == "Market Overview":
    try:
        market_overview_dashboard()
    except Exception as e:
        st.error(f"🚨 Error loading Market Overview Dashboard: {e}")

elif tab_selection == "Competitor Intelligence":
    try:
        competitor_intelligence_dashboard()
    except Exception as e:
        st.error(f"🚨 Error loading Competitor Intelligence Dashboard: {e}")

elif tab_selection == "Supplier Performance":
    try:
        supplier_performance_dashboard()
    except Exception as e:
        st.error(f"🚨 Error loading Supplier Performance Dashboard: {e}")

elif tab_selection == "State-Level Market Insights":
    try:
        state_level_market_insights()
    except Exception as e:
        st.error(f"🚨 Error loading State-Level Market Insights Dashboard: {e}")

elif tab_selection == "AI-Based Alerts & Forecasting":
    try:
        ai_based_alerts_forecasting()
    except Exception as e:
        st.error(f"🚨 Error loading AI-Based Alerts & Forecasting Dashboard: {e}")
