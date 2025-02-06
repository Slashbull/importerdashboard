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
    # List of candidate product categories.
    categories = ["Safawi", "Sukkari", "Sugar", "Phoenix", "Unmanufactured"]
    # Use fuzzy matching to find the best match.
    best_match = process.extractOne(mark, categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

def smart_apply_filters(df: pd.DataFrame):
    """
    Applies a smart, interconnected set of global filters to the DataFrame.
    Each filter's options are updated dynamically based on selections in the other filters.
    
    Available filters:
      - Year
      - Month
      - Consignee State
      - Consignee
      - Exporter
      - Product (derived from "Mark")
      
    The function returns:
      - The filtered DataFrame.
      - The unit column (fixed as "Tons").
    """
    st.sidebar.header("🔍 Global Data Filters (Smart)")
    
    # Work on a copy of the DataFrame so the original data remains intact.
    filtered_df = df.copy()
    
    # --- Step 0: Ensure the 'Product' column exists if "Mark" is present.
    if "Mark" in filtered_df.columns and "Product" not in filtered_df.columns:
        with st.spinner("Processing product categories..."):
            filtered_df["Product"] = filtered_df["Mark"].apply(lambda x: classify_mark(x))
    
    # Helper function to create a dynamic multiselect widget.
    def dynamic_multiselect(label: str, column: str, current_df: pd.DataFrame):
        if column not in current_df.columns:
            return None
        # Get sorted unique options available in the current filtered data.
        options = sorted(current_df[column].dropna().unique().tolist())
        # Include an "All" option at the beginning.
        options_with_all = ["All"] + options
        # Let the user choose; default selection is "All".
        selected = st.sidebar.multiselect(f"📌 {label}:", options=options_with_all, default=["All"])
        # If "All" is selected or nothing is selected, return the complete list.
        if "All" in selected or not selected:
            return options
        return selected

    # --- Step 1: Filter by Year.
    selected_years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if selected_years is not None:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
    
    # --- Step 2: Filter by Month.
    selected_months = dynamic_multiselect("Select Month", "Month", filtered_df)
    if selected_months is not None:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    
    # --- Step 3: Filter by Consignee State.
    selected_states = dynamic_multiselect("Select Consignee State", "Consignee State", filtered_df)
    if selected_states is not None:
        filtered_df = filtered_df[filtered_df["Consignee State"].isin(selected_states)]
    
    # --- Step 4: Filter by Consignee.
    selected_consignees = dynamic_multiselect("Select Consignee", "Consignee", filtered_df)
    if selected_consignees is not None:
        filtered_df = filtered_df[filtered_df["Consignee"].isin(selected_consignees)]
    
    # --- Step 5: Filter by Exporter.
    selected_exporters = dynamic_multiselect("Select Exporter", "Exporter", filtered_df)
    if selected_exporters is not None:
        filtered_df = filtered_df[filtered_df["Exporter"].isin(selected_exporters)]
    
    # --- Step 6: Filter by Product.
    selected_products = dynamic_multiselect("Select Product", "Product", filtered_df)
    if selected_products is not None:
        filtered_df = filtered_df[filtered_df["Product"].isin(selected_products)]
    
    # Ensure that the unit column ("Tons") is converted to numeric.
    unit_column = "Tons"
    if unit_column in filtered_df.columns:
        filtered_df[unit_column] = pd.to_numeric(filtered_df[unit_column], errors='coerce')
    
    return filtered_df, unit_column
