import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz  # Requires: pip install rapidfuzz

def classify_mark(mark: str, threshold: int = 70) -> str:
    """
    Classify the long 'Mark' string into a simplified product category using fuzzy matching.
    
    Parameters:
        mark (str): The original Mark string.
        threshold (int): The minimum score (0-100) required to consider a match.
        
    Returns:
        A simplified product category or "Other" if no match meets the threshold.
    """
    if not isinstance(mark, str):
        return "Unknown"
    mark_lower = mark.lower()
    # List of candidate product categories.
    categories = ["Safawi", "Sukkari", "Sugar", "Phoenix", "Unmanufactured"]
    # Use fuzzy matching to find the best match.
    best_match = process.extractOne(mark, categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

def apply_filters(df: pd.DataFrame):
    """
    Applies global filters to the DataFrame with real-time feedback and displays an
    active filters summary.
    
    Filters are provided for:
      - Consignee State
      - Month
      - Year
      - Consignee
      - Exporter
      - Product (automatically classified from the "Mark" column)
      
    Each filter includes an "All" option by default. When "All" is selected, the filter
    uses the full list of unique values.
    
    Returns:
      - The filtered DataFrame.
      - The unit column (which is fixed as "Tons").
    """
    st.sidebar.header("🔍 Global Data Filters")
    
    # Filter by Consignee State
    if "Consignee State" in df.columns:
        states = sorted(df["Consignee State"].dropna().unique().tolist())
        state_options = ["All"] + states
        selected_states = st.sidebar.multiselect("📌 Select State:", options=state_options, default=["All"])
        if "All" in selected_states:
            selected_states = states
    else:
        selected_states = []
    
    # Filter by Month
    if "Month" in df.columns:
        months = sorted(df["Month"].dropna().unique().tolist())
        month_options = ["All"] + months
        selected_months = st.sidebar.multiselect("📅 Select Month:", options=month_options, default=["All"])
        if "All" in selected_months:
            selected_months = months
    else:
        selected_months = []
    
    # Filter by Year
    if "Year" in df.columns:
        years = sorted(df["Year"].dropna().unique().tolist())
        year_options = ["All"] + years
        selected_years = st.sidebar.multiselect("📆 Select Year:", options=year_options, default=["All"])
        if "All" in selected_years:
            selected_years = years
    else:
        selected_years = []
    
    # Filter by Consignee
    if "Consignee" in df.columns:
        consignees = sorted(df["Consignee"].dropna().unique().tolist())
        consignee_options = ["All"] + consignees
        selected_consignees = st.sidebar.multiselect("🏢 Select Consignee:", options=consignee_options, default=["All"])
        if "All" in selected_consignees:
            selected_consignees = consignees
    else:
        selected_consignees = []
    
    # Filter by Exporter
    if "Exporter" in df.columns:
        exporters = sorted(df["Exporter"].dropna().unique().tolist())
        exporter_options = ["All"] + exporters
        selected_exporters = st.sidebar.multiselect("🚢 Select Exporter:", options=exporter_options, default=["All"])
        if "All" in selected_exporters:
            selected_exporters = exporters
    else:
        selected_exporters = []
    
    # Create and filter by Product using fuzzy matching on "Mark"
    if "Mark" in df.columns:
        if "Product" not in df.columns:
            df["Product"] = df["Mark"].apply(lambda x: classify_mark(x))
        products = sorted(df["Product"].dropna().unique().tolist())
        product_options = ["All"] + products
        selected_products = st.sidebar.multiselect("🔖 Select Product:", options=product_options, default=["All"])
        if "All" in selected_products:
            selected_products = products
    else:
        selected_products = []
    
    # We are using only the Tons column
    unit_column = "Tons"
    if unit_column in df.columns:
        df[unit_column] = pd.to_numeric(df[unit_column], errors='coerce')
    
    # Apply filters with a real-time spinner
    with st.spinner("Applying filters..."):
        filtered_df = df.copy()
        if "Consignee State" in df.columns:
            filtered_df = filtered_df[filtered_df["Consignee State"].isin(selected_states)]
        if "Month" in df.columns:
            filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
        if "Year" in df.columns:
            filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
        if "Consignee" in df.columns:
            filtered_df = filtered_df[filtered_df["Consignee"].isin(selected_consignees)]
        if "Exporter" in df.columns:
            filtered_df = filtered_df[filtered_df["Exporter"].isin(selected_exporters)]
        if "Product" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Product"].isin(selected_products)]
    
    # Display an active filters summary in the sidebar
    active_filters = {
        "State": selected_states,
        "Month": selected_months,
        "Year": selected_years,
        "Consignee": selected_consignees,
        "Exporter": selected_exporters,
        "Product": selected_products,
    }
    summary_text = "Active Filters:\n"
    for key, value in active_filters.items():
        summary_text += f"- {key}: {', '.join(map(str, value))}\n"
    st.sidebar.markdown(summary_text)

    return filtered_df, unit_column
