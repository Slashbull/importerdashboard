import streamlit as st
import pandas as pd
import polars as pl
from io import StringIO

# ---- Secure User Authentication ---- #
USERS = {"admin": "admin123"}  # Simple Username & Password

# ---- Session State Management ---- #
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

# ---- Login Page ---- #
def login():
    st.title("🔒 Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# ---- Logout Function ---- #
def logout():
    st.session_state["authenticated"] = False
    st.session_state["uploaded_file"] = None
    st.rerun()

# ---- File Upload Page ---- #
def file_upload():
    st.title("📂 Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            # Read and cache the file
            file_bytes = uploaded_file.getvalue()
            st.session_state["uploaded_file"] = file_bytes
            st.success("File uploaded successfully!")
            st.button("Proceed to Dashboard", on_click=lambda: st.rerun())
        except Exception as e:
            st.error(f"Error processing file: {e}")

# ---- Dashboard Page ---- #
def dashboard():
    st.title("📊 Importer Decision-Making Dashboard")
    st.sidebar.button("Logout", on_click=logout)
    
    # Load cached file if available
    if st.session_state["uploaded_file"]:
        df = pl.read_csv(StringIO(st.session_state["uploaded_file"].decode("utf-8")))
        st.write("### Preview of Uploaded Data")
        st.dataframe(df.head())
    else:
        st.warning("No file uploaded. Please upload a CSV file first.")

# ---- Main Application Logic ---- #
if not st.session_state["authenticated"]:
    login()
elif not st.session_state["uploaded_file"]:
    file_upload()
else:
    dashboard()

# Save file as core_system_foundation.py
