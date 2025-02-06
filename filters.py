import streamlit as st
import pandas as pd

def classify_mark(mark: str) -> str:
    """
    A simple classifier that extracts a product category from a long mark string.
    Uses basic keyword matching.
    """
    if not isinstance(mark, str):
        return "Unknown"
    mark_lower = mark.lower()
    if "safawi" in mark_lower:
        return "Safawi"
    if "sukkari" in mark_lower:
        return "Sukkari"
    if "sugar" in mark_lower:
        return "Sugar"
    if "phoenix" in mark_lower:
        return "Phoenix"
    if "unmanufactured" in mark_lower:
        return "Unmanufactured"
    return "Other"

def apply_filters(df: pd.DataFrame):
    st.sidebar.header("🔍 Global Data Filters")
    
    # Filter by Consignee State
    if "Consignee State" in df.columns:
        states = sorted(df["Consignee State"].dropna().unique().tolist())
        state_options = ["All"] + states
        selected_state = st.sidebar.multiselect("📌 Select State:", options=state_options, default=["All"])
        if "All" in selected_state:
            selected_state = states
    else:
        selected_state = []
    
    # Filter by Month
    if "Month" in df.columns:
        months = sorted(df["Month"].dropna().unique().tolist())
        month_options = ["All"] + months
        selected_month = st.sidebar.multiselect("📅 Select Month:", options=month_options, default=["All"])
        if "All" in selected_month:
            selected_month = months
    else:
        selected_month = []
    
    # Filter by Year
    if "Year" in df.columns:
        years = sorted(df["Year"].dropna().unique().tolist())
        year_options = ["All"] + years
        selected_year = st.sidebar.multiselect("📆 Select Year:", options=year_options, default=["All"])
        if "All" in selected_year:
            selected_year = years
    else:
        selected_year = []
    
    # Filter by Consignee
    if "Consignee" in df.columns:
        consignees = sorted(df["Consignee"].dropna().unique().tolist())
        consignee_options = ["All"] + consignees
        selected_consignee = st.sidebar.multiselect("🏢 Select Consignee:", options=consignee_options, default=["All"])
        if "All" in selected_consignee:
            selected_consignee = consignees
    else:
        selected_consignee = []
    
    # Filter by Exporter
    if "Exporter" in df.columns:
        exporters = sorted(df["Exporter"].dropna().unique().tolist())
        exporter_options = ["All"] + exporters
        selected_exporter = st.sidebar.multiselect("🚢 Select Exporter:", options=exporter_options, default=["All"])
        if "All" in selected_exporter:
            selected_exporter = exporters
    else:
        selected_exporter = []
    
    # Create a new "Product" column from "Mark" using classification
    if "Mark" in df.columns:
        if "Product" not in df.columns:
            df["Product"] = df["Mark"].apply(classify_mark)
        products = sorted(df["Product"].dropna().unique().tolist())
        product_options = ["All"] + products
        selected_product = st.sidebar.multiselect("🔖 Select Product:", options=product_options, default=["All"])
        if "All" in selected_product:
            selected_product = products
    else:
        selected_product = []
    
    # Since we're only using the Tons column, define unit_column as Tons
    unit_column = "Tons"
    if unit_column in df.columns:
        df[unit_column] = pd.to_numeric(df[unit_column], errors='coerce')
    
    # Apply the filters to create a filtered DataFrame
    filtered_df = df.copy()
    if "Consignee State" in df.columns:
        filtered_df = filtered_df[filtered_df["Consignee State"].isin(selected_state)]
    if "Month" in df.columns:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_month)]
    if "Year" in df.columns:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_year)]
    if "Consignee" in df.columns:
        filtered_df = filtered_df[filtered_df["Consignee"].isin(selected_consignee)]
    if "Exporter" in df.columns:
        filtered_df = filtered_df[filtered_df["Exporter"].isin(selected_exporter)]
    if "Product" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Product"].isin(selected_product)]
    
    return filtered_df, unit_column
