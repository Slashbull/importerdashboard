import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz  # pip install rapidfuzz
import re
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

# Predefined month ordering for sorting
MONTH_ORDER: dict[str, int] = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def clean_text(text: str) -> str:
    """
    Normalize text by converting to lowercase and removing non-alphabetic characters.
    
    Parameters:
        text (str): The text to clean.
    
    Returns:
        str: The cleaned text.
    """
    # Convert to lowercase and remove non-alphabetic characters (except whitespace)
    return re.sub(r'[^a-z\s]', '', text.lower()).strip()

def classify_mark(mark: str, threshold: int = 70) -> str:
    """
    Classify the 'Mark' string into a simplified product category using a two‑step approach:
    
      1. Dictionary matching on a cleaned version of the text.
      2. Fuzzy matching against a candidate list if no dictionary match is found.
    
    Parameters:
        mark (str): The original product description.
        threshold (int): Minimum fuzzy matching score (default is 70).
        
    Returns:
        str: A product category (e.g., "Ajwa", "Mabroom", "Safawi", etc.) or "Other".
    """
    if not isinstance(mark, str):
        return "Unknown"
    
    # Clean the text to help overcome spelling mistakes
    cleaned_mark = clean_text(mark)
    
    # Extended dictionary of product categories with associated keywords.
    # Order matters: more specific categories should be checked first.
    category_keywords = {
        "Ajwa": ["ajwa"],
        "Mabroom": ["mabroom"],
        "Safawi": ["safawi"],
        "Sukkari": ["sukkari"],
        "Rabia": ["rabia"],
        "Sugar": ["sugar"],
        "Phoenix": ["phoenix", "dactylifera"],
        "Unmanufactured": ["unmanufactured"],
        "Mixed": ["mixed"],
        "Fresh": ["fresh"],
        # Fallback generic category if the word "dates" is mentioned.
        "Dates": ["dates"]
    }
    
    # First, try dictionary matching on the cleaned text.
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in cleaned_mark:
                logger.info("Dictionary match: found keyword '%s' in mark '%s'; classifying as '%s'.", keyword, mark, category)
                return category
    
    # If no dictionary match is found, use fuzzy matching.
    candidate_categories = list(category_keywords.keys())
    best_match = process.extractOne(mark, candidate_categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        logger.info("Fuzzy match: '%s' classified as '%s' (score: %s).", mark, best_match[0], best_match[1])
        return best_match[0]
    
    return "Other"

def smart_apply_filters(df: pd.DataFrame):
    """
    Apply dynamic, interconnected filters to the DataFrame.
    
    Filters (shown in the sidebar):
      - Year
      - Month
      - Consignee State
      - Consignee
      - Exporter
      - Product (automatically derived from the 'Mark' column)
    
    If no filter is selected, all available options for that field are used.
    
    Returns:
        tuple: (filtered DataFrame, unit column as string ("Tons"))
    """
    st.sidebar.header("🔍 Global Data Filters")
    filtered_df = df.copy()
    
    # Automatically classify products using a fixed threshold of 70.
    if "Mark" in filtered_df.columns and "Product" not in filtered_df.columns:
        fixed_threshold = 70
        with st.spinner("Classifying products..."):
            filtered_df["Product"] = filtered_df["Mark"].apply(
                lambda x: classify_mark(x, threshold=fixed_threshold)
            )
    
    def dynamic_multiselect(label: str, column: str, current_df: pd.DataFrame):
        """
        Create a dynamic multiselect widget for the specified column.
        Returns all available options if the user makes no selection.
        
        Parameters:
            label (str): Label for the widget.
            column (str): The column name.
            current_df (pd.DataFrame): DataFrame on which to apply the filter.
        
        Returns:
            list: Selected options or full list if no selection.
        """
        if column not in current_df.columns:
            st.sidebar.error(f"Column '{column}' not found.")
            st.error(f"Missing column: {column}.")
            logger.error("Column '%s' is missing in the DataFrame.", column)
            return None
        options = current_df[column].dropna().unique().tolist()
        if column == "Month":
            options = sorted(options, key=lambda m: MONTH_ORDER.get(m, 99))
        else:
            options = sorted(options)
        selected = st.sidebar.multiselect(f"📌 {label}:", options, default=[], key=f"multiselect_{column}")
        return options if not selected else selected

    # Apply multiselect filters for each column.
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
    
    unit_column = "Tons"
    if unit_column in filtered_df.columns:
        filtered_df[unit_column] = pd.to_numeric(filtered_df[unit_column], errors="coerce")
    
    return filtered_df, unit_column
