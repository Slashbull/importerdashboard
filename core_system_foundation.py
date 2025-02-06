import streamlit as st
import pandas as pd
import hashlib
from market_overview import market_overview_dashboard

# ---- Core System Foundation ---- #

# ---- User Authentication ---- #
USERS = {"admin": "admin123"}

def hash_password(password: str) -> str:
    """Hash passwords using SHA-256 for security."""
    return hashlib.sha256(password.encode()).hexdigest()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    """User login system with modern UI."""
    st.markdown("""
    <style>
        .centered { text-align: center; }
        .stTextInput>div>div>input { text-align: center; }
        .stButton>button { width: 100%; border-radius: 8px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 class='centered'>🔒 Secure Login</h2>", unsafe_allow_html=True)
    username = st.text_input("👤 Username", key="login_username")
    password = st.text_input("🔑 Password", type="password", key="login_password")
    
    if st.button("🚀 Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("🚨 Invalid Username or Password")

def logout():
    """Logs out the user."""
    st.session_state["authenticated"] = False
    st.rerun()

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ---- Sidebar Navigation ---- #
st.sidebar.title("📌 Navigation")
tab_selection = st.sidebar.radio("Go to:", ["Upload Data", "Market Overview"])
st.sidebar.button("🔓 Logout", on_click=logout)

# ---- Upload Data Page ---- #
if "uploaded_data" in st.session_state:
    df = st.session_state["uploaded_data"]
    tab_selection = "Market Overview"
else:
    df = None
    tab_selection = st.sidebar.radio("📌 Navigation", ["Upload Data", "Market Overview"])
    st.markdown("<h2 class='centered'>📂 Upload Your Data</h2>", unsafe_allow_html=True)
    
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"))
    df = None
    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"], help="Upload a CSV file containing import data.")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success("✅ File uploaded successfully!")
    
    elif upload_option == "Google Sheet Link":
        sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
        sheet_name = st.text_input("📑 Enter Sheet Name:")
        if sheet_url and sheet_name:
            try:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                df = pd.read_csv(url)
                st.success(f"✅ Data loaded from sheet: {sheet_name}")
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")
    
    if df is not None:
        st.session_state["uploaded_data"] = df
        st.session_state["current_tab"] = "Market Overview"
        st.rerun()
        try:
            required_columns = ["SR NO.", "Job No.", "Consignee", "Exporter", "Mark", 
                                "Quanity (Kgs)", "Quanity (Tons)", "Month", "Year", "Consignee State"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"🚨 Missing Columns: {missing_columns}")
                st.stop()
            
            month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                         "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
            df["Quanity (Kgs)"] = df["Quanity (Kgs)"].astype(str).str.replace(" Kgs", "").str.replace(",", "").astype(float)
            df["Quanity (Tons)"] = df["Quanity (Tons)"].astype(str).str.replace(" tons", "").str.replace(",", "").astype(float)
            df["Month"] = df["Month"].astype(str).str[:3]
            df["Consignee State"].fillna("Unknown", inplace=True)
            
            st.success("✅ Data processing completed.")
            
            # ---- Download Processed Data ---- #
            csv = df.loc[:, ~df.columns.str.contains('^Unnamed')].to_csv(index=False).encode('utf-8')
            st.sidebar.download_button("📥 Download Processed Data", csv, "processed_data.csv", "text/csv")
        
        except Exception as e:
            st.error(f"🚨 Error processing file: {e}")

# ---- Market Overview Page ---- #
elif tab_selection == "Market Overview":
    if df is None:
        st.warning("⚠️ No data available. Please upload a dataset first.")
    else:
        market_overview_dashboard(df)
