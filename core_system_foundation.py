import streamlit as st
import pandas as pd
import hashlib

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
            st.experimental_rerun()
        else:
            st.error("🚨 Invalid Username or Password")

def logout():
    """Logs out the user."""
    st.session_state["authenticated"] = False
    st.experimental_rerun()

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ---- Sidebar Navigation ---- #
st.sidebar.title("📌 Navigation")
tab_selection = st.sidebar.radio("Go to:", ["Upload Data", "Market Overview"])
st.sidebar.button("🔓 Logout", on_click=logout)

# ---- Upload Data Page ---- #
if tab_selection == "Upload Data":
    st.markdown("<h2 class='centered'>📂 Upload Your Data</h2>", unsafe_allow_html=True)
    
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"))
    df = None
    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("📥 Upload CSV File", type=["csv"], help="Upload a CSV file containing import data.")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            
            # Standardize Month Names
            month_map = {"Jan": "Jan", "Feb": "Feb", "Mar": "Mar", "Apr": "Apr", "May": "May", "Jun": "Jun", "Jul": "Jul", "Aug": "Aug", "Sep": "Sep", "Oct": "Oct", "Nov": "Nov", "Dec": "Dec"}
            if "Month" in df.columns:
                df["Month"] = df["Month"].astype(str).map(month_map)
            
            # Ensure Column Consistency
            if "Consignee State" in df.columns:
                df.rename(columns={"Consignee State": "State"}, inplace=True)
            
            # Drop Unnecessary Columns
            if "SR NO." in df.columns:
                df.drop(columns=["SR NO."], inplace=True)
            
            st.session_state["uploaded_data"] = df
            st.success("✅ File uploaded and cleaned successfully! Redirecting...")
            st.experimental_rerun()
    
    elif upload_option == "Google Sheet Link":
        sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
        sheet_name = st.text_input("📑 Enter Sheet Name:")
        if sheet_url and sheet_name:
            try:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                df = pd.read_csv(url)
                
                # Standardize Month Names
                if "Month" in df.columns:
                    df["Month"] = df["Month"].astype(str).map(month_map)
                
                # Ensure Column Consistency
                if "Consignee State" in df.columns:
                    df.rename(columns={"Consignee State": "State"}, inplace=True)
                
                # Drop Unnecessary Columns
                if "SR NO." in df.columns:
                    df.drop(columns=["SR NO."], inplace=True)
                
                st.session_state["uploaded_data"] = df
                st.success(f"✅ Data loaded and cleaned from sheet: {sheet_name}. Redirecting...")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")

# ---- Market Overview Placeholder ---- #
elif tab_selection == "Market Overview":
    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
    else:
        st.write("### 🚧 Market Overview Dashboard is under construction.")
        st.info("Key metrics and trends will be displayed here.")

        # ---- Download Processed Data ---- #
        df = st.session_state["uploaded_data"]
        csv = df.loc[:, ~df.columns.str.contains('^Unnamed')].to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Download Processed Data", csv, "processed_data.csv", "text/csv")
