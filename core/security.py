import streamlit as st
import hashlib
import os
from io import BytesIO

# ---- Security System ---- #

# ---- Secure Hashing for Passwords ---- #
def hash_password(password: str) -> str:
    """Hash passwords using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

# ---- Secure File Upload Validation ---- #
ALLOWED_EXTENSIONS = {"csv"}

def validate_uploaded_file(uploaded_file) -> bool:
    """Validate uploaded files for security compliance."""
    if uploaded_file is None:
        st.error("🚨 No file uploaded.")
        return False
    
    # Check file extension
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        st.error(f"🚨 Invalid file type: {file_extension.upper()} (Only CSV allowed)")
        return False
    
    return True

# ---- Secure Session Handling ---- #
def secure_session():
    """Ensure session integrity and prevent unauthorized access."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        st.warning("🔒 Access restricted. Please log in.")
        st.stop()

# Save file as security.py
