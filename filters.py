import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz  # Requires: pip install rapidfuzz

# Predefined month ordering for sorting
MONTH_ORDER = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
               "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

def classify_mark(mark: str, threshold: int = 70) -> str:
    """
    Classify a product description (Mark) using fuzzy matching.
    Returns the best candidate if its score is >= threshold, otherwise "Other".
    """
    if not isinstance(mark, str):
        return "Unknown"
    # Candidate categories (can be made configurable)
    categories = ["Safawi", "Sukkari", "Sugar", "Phoenix", "Unmanufactured"]
    best_match = process.extractOne(mark, categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

def smart_apply_filters(df: pd.DataFrame):
    """
    Apply dynamic, interconnected filters to the DataFrame.
    Filters: Year, Month, Consignee State, Consignee, Exporter, Product.
    Returns the filtered DataFrame and the unit column ("Tons").
    """
    st.sidebar.header("🔍 Global Data Filters (Smart)")

    # Work on a copy to avoid modifying the original DataFrame
    filtered_df = df.copy()

    # Enhanced product classification with an interactive fuzzy matching threshold
    if "Mark" in filtered_df.columns and "Product" not in filtered_df.columns:
        threshold_value = st.sidebar.slider("Set Fuzzy Matching Threshold", 50, 100, 70, step=5)
        with st.spinner("Processing product categories..."):
            filtered_df["Product"] = filtered_df["Mark"].apply(lambda x: classify_mark(x, threshold=threshold_value))

    def dynamic_multiselect(label: str, column: str, current_df: pd.DataFrame):
        """
        Create a dynamic multiselect widget for a given column.
        Returns a list of selected values (or all values if "All" is chosen).
        """
        if column not in current_df.columns:
            st.sidebar.error(f"Column '{column}' not found.")
            st.error(f"Missing column: {column}. Please check your dataset.")
            return None

        # Extract and sort options
        options = current_df[column].dropna().unique().tolist()
        if column == "Month":
            options = sorted(options, key=lambda m: MONTH_ORDER.get(m, 99))
        elif column == "Period":
            try:
                options = sorted(options)
            except Exception as e:
                st.warning(f"Sorting Period column failed: {e}")
        else:
            options = sorted(options)
        
        if not options:
            st.sidebar.warning(f"No options available for {column}.")
            return []
        
        options_with_all = ["All"] + options
        selected = st.sidebar.multiselect(f"📌 {label}:", options_with_all, default=["All"])
        if "All" in selected or not selected:
            return options
        return selected

    # Sequentially apply filters
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
