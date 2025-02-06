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
    # Candidate categories could be later parameterized or updated from an external source.
    categories = ["Safawi", "Sukkari", "Sugar", "Phoenix", "Unmanufactured"]
    best_match = process.extractOne(mark, categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

def smart_apply_filters(df: pd.DataFrame):
    """
    Applies a smart, interconnected set of global filters to the DataFrame.
    Each filter's options update dynamically based on selections in the other filters.
    
    Available filters:
      - Year
      - Month
      - Consignee State
      - Consignee
      - Exporter
      - Product (derived from "Mark")
      
    Returns:
      - The filtered DataFrame.
      - The unit column (fixed as "Tons").
    """
    st.sidebar.header("🔍 Global Data Filters (Smart)")

    # Work on a copy to avoid modifying the original DataFrame
    filtered_df = df.copy()

    # Ensure the 'Product' column exists if "Mark" is present
    if "Mark" in filtered_df.columns and "Product" not in filtered_df.columns:
        with st.spinner("Processing product categories..."):
            # Allow an interactive threshold control for fuzzy matching.
            threshold_value = st.sidebar.slider(
                "Set Fuzzy Matching Threshold", min_value=50, max_value=100, value=70, step=5
            )
            filtered_df["Product"] = filtered_df["Mark"].apply(
                lambda x: classify_mark(x, threshold=threshold_value)
            )

    def dynamic_multiselect(label: str, column: str, current_df: pd.DataFrame):
        """
        Create a dynamic multiselect widget for a specific column.
        
        Parameters:
            label (str): The display label for the multiselect.
            column (str): The DataFrame column to filter on.
            current_df (pd.DataFrame): The current subset of data.
            
        Returns:
            A list of selected values, or the full list if "All" is selected or nothing is selected.
        """
        if column not in current_df.columns:
            st.sidebar.error(f"Column '{column}' not found in data.")
            return None
        options = sorted(current_df[column].dropna().unique().tolist())
        if not options:
            return []
        options_with_all = ["All"] + options
        selected = st.sidebar.multiselect(f"📌 {label}:", options=options_with_all, default=["All"])
        if "All" in selected or not selected:
            return options
        return selected

    # Apply filters sequentially
    selected_years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if selected_years is not None:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
    
    selected_months = dynamic_multiselect("Select Month", "Month", filtered_df)
    if selected_months is not None:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    
    selected_states = dynamic_multiselect("Select Consignee State", "Consignee State", filtered_df)
    if selected_states is not None:
        filtered_df = filtered_df[filtered_df["Consignee State"].isin(selected_states)]
    
    selected_consignees = dynamic_multiselect("Select Consignee", "Consignee", filtered_df)
    if selected_consignees is not None:
        filtered_df = filtered_df[filtered_df["Consignee"].isin(selected_consignees)]
    
    selected_exporters = dynamic_multiselect("Select Exporter", "Exporter", filtered_df)
    if selected_exporters is not None:
        filtered_df = filtered_df[filtered_df["Exporter"].isin(selected_exporters)]
    
    selected_products = dynamic_multiselect("Select Product", "Product", filtered_df)
    if selected_products is not None:
        filtered_df = filtered_df[filtered_df["Product"].isin(selected_products)]
    
    # Ensure 'Tons' is numeric
    unit_column = "Tons"
    if unit_column in filtered_df.columns:
        filtered_df[unit_column] = pd.to_numeric(filtered_df[unit_column], errors='coerce')
    
    return filtered_df, unit_column
