import streamlit as st
import pandas as pd

def apply_filters(df: pd.DataFrame):
    st.sidebar.header("🔍 Global Data Filters")
    
    # Consignee State Filter
    if "Consignee State" in df.columns:
        states = sorted(df["Consignee State"].unique().tolist())
        state_options = ["All"] + states
        selected_state = st.sidebar.multiselect("📌 Select State:", options=state_options, default=["All"])
        if "All" in selected_state:
            selected_state = states
    else:
        selected_state = []
    
    # Month Filter
    if "Month" in df.columns:
        months = sorted(df["Month"].unique().tolist())
        month_options = ["All"] + months
        selected_month = st.sidebar.multiselect("📅 Select Month:", options=month_options, default=["All"])
        if "All" in selected_month:
            selected_month = months
    else:
        selected_month = []
    
    # Year Filter
    if "Year" in df.columns:
        years = sorted(df["Year"].unique().tolist())
        year_options = ["All"] + years
        selected_year = st.sidebar.multiselect("📆 Select Year:", options=year_options, default=["All"])
        if "All" in selected_year:
            selected_year = years
    else:
        selected_year = []
    
    # Consignee Filter
    if "Consignee" in df.columns:
        consignees = sorted(df["Consignee"].unique().tolist())
        consignee_options = ["All"] + consignees
        selected_consignee = st.sidebar.multiselect("🏢 Select Consignee:", options=consignee_options, default=["All"])
        if "All" in selected_consignee:
            selected_consignee = consignees
    else:
        selected_consignee = []
    
    # Exporter Filter
    if "Exporter" in df.columns:
        exporters = sorted(df["Exporter"].unique().tolist())
        exporter_options = ["All"] + exporters
        selected_exporter = st.sidebar.multiselect("🚢 Select Exporter:", options=exporter_options, default=["All"])
        if "All" in selected_exporter:
            selected_exporter = exporters
    else:
        selected_exporter = []
    
    # Mark Filter
    if "Mark" in df.columns:
        marks = sorted(df["Mark"].unique().tolist())
        mark_options = ["All"] + marks
        selected_mark = st.sidebar.multiselect("🔖 Select Mark:", options=mark_options, default=["All"])
        if "All" in selected_mark:
            selected_mark = marks
    else:
        selected_mark = []
    
    # Unit Toggle
    unit_toggle = st.sidebar.radio("⚖️ Select Unit:", ("Kgs", "Tons"))
    unit_column = "Kgs" if unit_toggle == "Kgs" else "Tons"
    
    # Apply filters to the data
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
    
    # Convert selected unit column to numeric
    if unit_column in filtered_df.columns:
        filtered_df[unit_column] = pd.to_numeric(filtered_df[unit_column], errors='coerce')
    
    return filtered_df, unit_column
