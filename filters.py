import streamlit as st
import pandas as pd

# ---- Filters Module ---- #
def apply_filters(df):
    st.sidebar.header("🔍 Data Filters")
    
    # State Filter
    states = df["Consignee State"].unique().tolist()
    selected_state = st.sidebar.multiselect("📌 Select State:", states, default=states)
    
    # Month Filter
    months = df["Month"].unique().tolist()
    selected_month = st.sidebar.multiselect("📅 Select Month:", months, default=months)
    
    # Year Filter
    years = df["Year"].unique().tolist()
    selected_year = st.sidebar.multiselect("📆 Select Year:", years, default=years)
    
    # Consignee Filter
    consignees = df["Consignee"].unique().tolist()
    selected_consignee = st.sidebar.multiselect("🏢 Select Consignee:", consignees, default=consignees)
    
    # Exporter Filter
    exporters = df["Exporter"].unique().tolist()
    selected_exporter = st.sidebar.multiselect("🚢 Select Exporter:", exporters, default=exporters)
    
    # Mark Filter
    marks = df["Mark"].unique().tolist()
    selected_mark = st.sidebar.multiselect("🔖 Select Mark:", marks, default=marks)
    
    # Toggle between Kgs and Tons
    unit_toggle = st.sidebar.radio("⚖️ Select Unit:", ("Kgs", "Tons"))
    unit_column = "Kgs" if unit_toggle == "Kgs" else "Tons"
    
    # Apply Filters
    filtered_df = df[
        (df["Consignee State"].isin(selected_state)) &
        (df["Month"].isin(selected_month)) &
        (df["Year"].isin(selected_year)) &
        (df["Consignee"].isin(selected_consignee)) &
        (df["Exporter"].isin(selected_exporter)) &
        (df["Mark"].isin(selected_mark))
    ]
    
    # Convert the selected unit column to numeric
    filtered_df[unit_column] = pd.to_numeric(filtered_df[unit_column], errors='coerce')
    
    return filtered_df, unit_column
