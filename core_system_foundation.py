import streamlit as st
import pandas as pd
import requests
from io import StringIO
from market_overview import market_overview_dashboard

# ---- Core System Foundation ---- #

# Sidebar Navigation with Login
st.sidebar.title("📌 Navigation")
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    username = st.sidebar.text_input("👤 Username", key="login_username")
    password = st.sidebar.text_input("🔑 Password", type="password", key="login_password")
    if st.sidebar.button("🚀 Login"):
        if username == "admin" and password == "admin123":
            st.session_state["authenticated"] = True
            st.session_state["current_tab"] = "Market Overview"
            st.query_params(tab="Market Overview")
        else:
            st.sidebar.error("🚨 Invalid Username or Password")
    st.stop()

st.sidebar.success("✅ Logged in")
tab_selection = st.sidebar.radio("Go to:", ["Upload Data", "Market Overview"])
st.sidebar.button("🔓 Logout", on_click=lambda: st.session_state.update({"authenticated": False, "uploaded_data": None}))

# ---- Upload Data Page ---- #
if tab_selection == "Upload Data":
    st.markdown("<h2 class='centered'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"))
    df = None
    
    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"], help="Upload a CSV file containing import data.")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.session_state["uploaded_data"] = df
            st.success("✅ File uploaded successfully!")
    
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
                df = pd.read_csv(StringIO(response.text))
                
                # Validate data
                if df.empty:
                    st.error("🚨 The sheet is empty or the sheet name is incorrect.")
                else:
                    st.session_state["uploaded_data"] = df
                    st.success(f"✅ Data loaded successfully from sheet: {sheet_name}")
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")

# ---- Market Overview Integration ---- #
elif tab_selection == "Market Overview":
    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
    else:
        df = st.session_state["uploaded_data"]
        market_overview_dashboard(df)
        
        # ---- Download Processed Data ---- #
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Download Processed Data", csv, "processed_data.csv", "text/csv")
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from market_overview import market_overview_dashboard

# ---- Core System Foundation ---- #

# Sidebar Navigation with Login
st.sidebar.title("📌 Navigation")
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    username = st.sidebar.text_input("👤 Username", key="login_username")
    password = st.sidebar.text_input("🔑 Password", type="password", key="login_password")
    if st.sidebar.button("🚀 Login"):
        if username == "admin" and password == "admin123":
            st.session_state["authenticated"] = True
            st.session_state["current_tab"] = "Market Overview"
            st.query_params(tab="Market Overview")
        else:
            st.sidebar.error("🚨 Invalid Username or Password")
    st.stop()

st.sidebar.success("✅ Logged in")
tab_selection = st.sidebar.radio("Go to:", ["Upload Data", "Market Overview"])
st.sidebar.button("🔓 Logout", on_click=lambda: st.session_state.update({"authenticated": False, "uploaded_data": None}))

# ---- Upload Data Page ---- #
if tab_selection == "Upload Data":
    st.markdown("<h2 class='centered'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"))
    df = None
    
    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"], help="Upload a CSV file containing import data.")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.session_state["uploaded_data"] = df
            st.success("✅ File uploaded successfully!")
    
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
                df = pd.read_csv(StringIO(response.text))
                
                # Validate data
                if df.empty:
                    st.error("🚨 The sheet is empty or the sheet name is incorrect.")
                else:
                    st.session_state["uploaded_data"] = df
                    st.success(f"✅ Data loaded successfully from sheet: {sheet_name}")
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")

# ---- Market Overview Integration ---- #
elif tab_selection == "Market Overview":
    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
    else:
        df = st.session_state["uploaded_data"]
        market_overview_dashboard(df)
        
        # ---- Download Processed Data ---- #
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Download Processed Data", csv, "processed_data.csv", "text/csv")
