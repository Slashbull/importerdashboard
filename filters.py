import streamlit as st
import pandas as pd

def apply_filters(df: pd.DataFrame):
    st.sidebar.header("🔍 Global Data Filters")
    
    # Only display filters if columns exist
    states = df["Consignee State"].unique().tolist() if "Consignee State" in df.columns else []
    selected_state = st.sidebar.multiselect("📌 Select State:", states, default=states)
    
    months = df["Month"].unique().tolist() if "Month" in df.columns else []
    selected_month = st.sidebar.multiselect("📅 Select Month:", months, default=months)
    
    years = df["Year"].unique().tolist() if "Year" in df.columns else []
    selected_year = st.sidebar.multiselect("📆 Select Year:", years, default=years)
    
    consignees = df["Consignee"].unique().tolist() if "Consignee" in df.columns else []
    selected_consignee = st.sidebar.multiselect("🏢 Select Consignee:", consignees, default=consignees)
    
    exporters = df["Exporter"].unique().tolist() if "Exporter" in df.columns else []
    selected_exporter = st.sidebar.multiselect("🚢 Select Exporter:", exporters, default=exporters)
    
    marks = df["Mark"].unique().tolist() if "Mark" in df.columns else []
    selected_mark = st.sidebar.multiselect("🔖 Select Mark:", marks, default=marks)
    
    unit_toggle = st.sidebar.radio("⚖️ Select Unit:", ("Kgs", "Tons"))
    unit_column = "Kgs" if unit_toggle == "Kgs" else "Tons"
    
    # Apply filters to data (if the column exists)
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
    if "Mark" in df.columns:
        filtered_df = filtered_df[filtered_df["Mark"].isin(selected_mark)]
    
    # Ensure the selected unit column is numeric
    if unit_column in filtered_df.columns:
        filtered_df[unit_column] = pd.to_numeric(filtered_df[unit_column], errors='coerce')
    
    return filtered_df, unit_column
