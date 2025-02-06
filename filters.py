import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz  # Requires: pip install rapidfuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def generate_candidate_categories(df: pd.DataFrame, num_clusters: int = 5) -> list:
    """
    Automatically generate candidate product categories from the 'Mark' column using TF‑IDF and K‑Means.
    
    Parameters:
      - df: DataFrame containing a 'Mark' column.
      - num_clusters: Number of clusters (candidate categories) to form.
    
    Returns:
      A list of candidate category labels.
    """
    marks = df['Mark'].dropna().tolist()
    if not marks:
        return ["Other"]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(marks)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    candidate_categories = []
    for i in range(num_clusters):
        # Use the top 5 terms in each cluster as the candidate label
        top_terms = [terms[ind] for ind in order_centroids[i, :5]]
        label = " / ".join(top_terms)
        candidate_categories.append(label)
    
    return candidate_categories

def classify_mark(mark: str, candidate_categories: list = None, threshold: int = 70) -> str:
    """
    Classify the long 'Mark' string into a simplified product category using fuzzy matching.
    
    Parameters:
        mark (str): The original Mark string.
        candidate_categories (list): Candidate product categories to match against. If None, a default list is used.
        threshold (int): The minimum matching score (0-100) required to accept a match.
        
    Returns:
        A simplified product category or "Other" if no match meets the threshold.
    """
    if not isinstance(mark, str):
        return "Unknown"
    # If candidate_categories is not provided, use a fallback default list.
    if candidate_categories is None:
        candidate_categories = ["Safawi", "Sukkari", "Sugar", "Phoenix", "Unmanufactured"]
    best_match = process.extractOne(mark, candidate_categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

def apply_filters(df: pd.DataFrame):
    """
    Applies global filters to the DataFrame with real-time feedback and displays an
    active filters summary. For each filter, an "All" option is provided by default.
    
    Filters are applied for:
      - Consignee State
      - Month
      - Year
      - Consignee
      - Exporter
      - Product (automatically classified from the "Mark" column)
      
    If a user deselects all options for any filter, it automatically defaults to the full list.
    
    Returns:
      - The filtered DataFrame.
      - The unit column (fixed as "Tons").
    """
    st.sidebar.header("🔍 Global Data Filters")
    
    def ensure_selection(selected, full_list):
        """Return the full list if selection is empty."""
        if not selected or len(selected) == 0:
            return full_list
        return selected

    # --- Filter by Consignee State ---
    if "Consignee State" in df.columns:
        states = sorted(df["Consignee State"].dropna().unique().tolist())
        state_options = ["All"] + states
        selected_states = st.sidebar.multiselect("📌 Select State:", options=state_options, default=["All"])
        if "All" in selected_states:
            selected_states = states
        selected_states = ensure_selection(selected_states, states)
    else:
        selected_states = []

    # --- Filter by Month ---
    if "Month" in df.columns:
        months = sorted(df["Month"].dropna().unique().tolist())
        month_options = ["All"] + months
        selected_months = st.sidebar.multiselect("📅 Select Month:", options=month_options, default=["All"])
        if "All" in selected_months:
            selected_months = months
        selected_months = ensure_selection(selected_months, months)
    else:
        selected_months = []

    # --- Filter by Year ---
    if "Year" in df.columns:
        years = sorted(df["Year"].dropna().unique().tolist())
        # Convert years to strings for display purposes.
        year_options = ["All"] + [str(y) for y in years]
        selected_years = st.sidebar.multiselect("📆 Select Year:", options=year_options, default=["All"])
        if "All" in selected_years:
            selected_years = [str(y) for y in years]
        selected_years = ensure_selection(selected_years, [str(y) for y in years])
    else:
        selected_years = []

    # --- Filter by Consignee ---
    if "Consignee" in df.columns:
        consignees = sorted(df["Consignee"].dropna().unique().tolist())
        consignee_options = ["All"] + consignees
        selected_consignees = st.sidebar.multiselect("🏢 Select Consignee:", options=consignee_options, default=["All"])
        if "All" in selected_consignees:
            selected_consignees = consignees
        selected_consignees = ensure_selection(selected_consignees, consignees)
    else:
        selected_consignees = []

    # --- Filter by Exporter ---
    if "Exporter" in df.columns:
        exporters = sorted(df["Exporter"].dropna().unique().tolist())
        exporter_options = ["All"] + exporters
        selected_exporters = st.sidebar.multiselect("🚢 Select Exporter:", options=exporter_options, default=["All"])
        if "All" in selected_exporters:
            selected_exporters = exporters
        selected_exporters = ensure_selection(selected_exporters, exporters)
    else:
        selected_exporters = []

    # --- Filter by Product ---
    if "Mark" in df.columns:
        # If the "Product" column doesn't exist, generate it automatically.
        if "Product" not in df.columns:
            # Generate candidate categories automatically.
            candidate_categories = generate_candidate_categories(df, num_clusters=5)
            df["Product"] = df["Mark"].apply(lambda x: classify_mark(x, candidate_categories))
        products = sorted(df["Product"].dropna().unique().tolist())
        product_options = ["All"] + products
        selected_products = st.sidebar.multiselect("🔖 Select Product:", options=product_options, default=["All"])
        if "All" in selected_products:
            selected_products = products
        selected_products = ensure_selection(selected_products, products)
    else:
        selected_products = []
    
    # Define the unit column (fixed as "Tons")
    unit_column = "Tons"
    if unit_column in df.columns:
        df[unit_column] = pd.to_numeric(df[unit_column], errors='coerce')
    
    # Apply filters (with a loading spinner)
    with st.spinner("Applying filters..."):
        filtered_df = df.copy()
        if "Consignee State" in df.columns:
            filtered_df = filtered_df[filtered_df["Consignee State"].isin(selected_states)]
        if "Month" in df.columns:
            filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
        if "Year" in df.columns:
            filtered_df = filtered_df[filtered_df["Year"].astype(str).isin(selected_years)]
        if "Consignee" in df.columns:
            filtered_df = filtered_df[filtered_df["Consignee"].isin(selected_consignees)]
        if "Exporter" in df.columns:
            filtered_df = filtered_df[filtered_df["Exporter"].isin(selected_exporters)]
        if "Product" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Product"].isin(selected_products)]
    
    # Display an active filters summary in the sidebar.
    active_filters = {
        "State": selected_states,
        "Month": selected_months,
        "Year": selected_years,
        "Consignee": selected_consignees,
        "Exporter": selected_exporters,
        "Product": selected_products,
    }
    summary_text = "Active Filters:\n\n"
    for key, value in active_filters.items():
        summary_text += f"- **{key}**: {', '.join(map(str, value))}\n"
    st.sidebar.markdown(summary_text)

    return filtered_df, unit_column
