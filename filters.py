import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz  # Requires: pip install rapidfuzz
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -------------------------------------
# Fuzzy Matching Function for Products
# -------------------------------------
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
    # Predefined candidate categories; can be parameterized in future.
    categories = ["Safawi", "Sukkari", "Sugar", "Phoenix", "Unmanufactured"]
    best_match = process.extractOne(mark, categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

# -------------------------------------
# Main Filter Function
# -------------------------------------
def smart_apply_filters(df: pd.DataFrame):
    """
    Applies a smart, interconnected set of global filters to the DataFrame.
    Each filter's options update dynamically based on selections in the other filters.
    
    Available filters:
      - Year (defaults to the latest year)
      - Month (defaults to the months in the latest year)
      - Consignee State
      - Consignee
      - Exporter
      - Product (derived from "Mark")
      
    Returns:
      - The filtered DataFrame.
      - The unit column (fixed as "Tons").
    """
    st.sidebar.header("🔍 Global Data Filters (Smart)")

    # Work on a copy so as not to modify original data.
    filtered_df = df.copy()

    # ---------------------------
    # Enhanced Fuzzy Matching for Product Classification
    # ---------------------------
    if "Mark" in filtered_df.columns and "Product" not in filtered_df.columns:
        with st.spinner("Processing product categories..."):
            threshold_value = st.sidebar.slider(
                "Fuzzy Matching Threshold", min_value=50, max_value=100, value=70, step=5,
                help="Adjust the threshold for classifying product descriptions."
            )
            filtered_df["Product"] = filtered_df["Mark"].apply(
                lambda x: classify_mark(x, threshold=threshold_value)
            )

    # Predefine month order for proper chronological sorting.
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    # ---------------------------
    # Dynamic Multiselect Helper Function with Error Handling
    # ---------------------------
    def dynamic_multiselect(label: str, column: str, current_df: pd.DataFrame, default_selection=None):
        """
        Create a dynamic multiselect widget for filtering a specific column.
        
        Parameters:
            label (str): Label to display.
            column (str): DataFrame column to filter.
            current_df (pd.DataFrame): Current data subset.
            default_selection (list): Preselected default options.
            
        Returns:
            List of selected values (defaults to all options if "All" is selected or no selection made).
        """
        if column not in current_df.columns:
            st.sidebar.error(f"Column '{column}' not found.")
            logger.warning(f"Column '{column}' missing in data.")
            return None
        try:
            options = sorted(current_df[column].dropna().unique().tolist())
        except Exception as e:
            st.sidebar.error(f"Error getting unique options for '{column}': {e}")
            logger.exception("Error in dynamic_multiselect for column '%s': %s", column, e)
            return None

        if column == "Month":
            # Order months chronologically using month_order
            options = sorted(options, key=lambda m: month_order.get(m, 99))
        # Determine default selection:
        if default_selection is None:
            # For Year: default to the latest year; for Month: default to months of the latest year.
            if column == "Year":
                try:
                    default_selection = [str(max([int(x) for x in options]))]
                except Exception:
                    default_selection = ["All"]
            elif column == "Month" and "Year" in current_df.columns:
                # Get latest year and select months corresponding to that year.
                try:
                    latest_year = str(max([int(x) for x in current_df["Year"].dropna().unique()]))
                    months_in_latest = current_df[current_df["Year"].astype(str) == latest_year]["Month"].unique().tolist()
                    default_selection = sorted(months_in_latest, key=lambda m: month_order.get(m, 99))
                except Exception:
                    default_selection = ["All"]
            else:
                default_selection = ["All"]

        options_with_all = ["All"] + options
        selected = st.sidebar.multiselect(f"📌 {label}:", options=options_with_all, default=default_selection)
        if "All" in selected or not selected:
            return options
        return selected

    # ---------------------------
    # Customizable Default Selections for Each Filter
    # ---------------------------
    # Year: default to latest year available.
    selected_years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if selected_years is not None:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]

    # Month: default to months corresponding to the latest year.
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
    
    # ---------------------------
    # Ensure Data Integrity
    # ---------------------------
    unit_column = "Tons"
    if unit_column in filtered_df.columns:
        filtered_df[unit_column] = pd.to_numeric(filtered_df[unit_column], errors='coerce')
    
    return filtered_df, unit_column
