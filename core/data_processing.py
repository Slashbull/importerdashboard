import streamlit as st
import polars as pl
from io import StringIO

# ---- Data Processing System ---- #

REQUIRED_COLUMNS = [
    "SR NO.", "Job No.", "Consignee", "Exporter", "Mark", "Quanity (Kgs)", "Quanity (Tons)", "Month", "Year", "Consignee State"
]

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

# ---- Data Validation ---- #
def validate_data(df: pl.DataFrame) -> bool:
    """Check if required columns exist and data is valid."""
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        st.error(f"🚨 Missing Required Columns: {missing_columns}")
        return False
    return True

# ---- Data Cleaning ---- #
def clean_data(df: pl.DataFrame) -> pl.DataFrame:
    """Perform cleaning operations on the dataset."""
    # Ensure required columns exist before processing
    if not validate_data(df):
        return None
    
    # Convert 'Quanity (Kgs)' and 'Quanity (Tons)' to numeric
    if "Quanity (Kgs)" in df.columns:
        df = df.with_columns(pl.col("Quanity (Kgs)").str.replace(" Kgs", "").cast(pl.Float64))
    if "Quanity (Tons)" in df.columns:
        df = df.with_columns(pl.col("Quanity (Tons)").str.replace(" tons", "").cast(pl.Float64))
    
    # Convert Month to Numeric
    if "Month" in df.columns:
        df = df.with_columns(pl.col("Month").replace(MONTH_MAP))
    
    # Fill missing values
    df = df.fill_null("Unknown")
    
    return df

# ---- Data Processing Function ---- #
@st.cache_data(max_entries=10)
def process_data(file) -> pl.DataFrame:
    """Load, clean, and validate uploaded data."""
    try:
        df = pl.read_csv(StringIO(file.decode("utf-8")))
        cleaned_df = clean_data(df)
        if cleaned_df is None:
            return None
        st.success("✅ Data successfully processed!")
        return cleaned_df
    except Exception as e:
        st.error(f"🚨 Error processing file: {e}")
        return None

# Save file as data_processing.py
