import streamlit as st
import polars as pl
from io import StringIO

# ---- Smart Caching System ---- #

def cache_processed_data(file):
    """Load, process, and cache dataset intelligently."""
    if "cached_data" in st.session_state and st.session_state["cached_file"] == file:
        return st.session_state["cached_data"]
    
    try:
        df = pl.read_csv(StringIO(file.decode("utf-8")))
        st.session_state["cached_file"] = file  # Store the latest uploaded file
        st.session_state["cached_data"] = df  # Store processed data
        return df
    except Exception as e:
        st.error(f"🚨 Error processing file: {e}")
        return None

def clear_cache():
    """Clear cached data when a new file is uploaded."""
    if "cached_data" in st.session_state:
        del st.session_state["cached_data"]
    if "cached_file" in st.session_state:
        del st.session_state["cached_file"]

# Save file as caching.py
