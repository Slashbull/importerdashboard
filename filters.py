import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz  # Requires: pip install rapidfuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# -----------------------------------------------------------------------------
# Automatic Candidate Categories Generation
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def generate_candidate_categories(df: pd.DataFrame, num_clusters: int = 5) -> list:
    """
    Automatically generate candidate product categories from the 'Mark' column
    using TF‑IDF vectorization and K‑Means clustering.
    
    Parameters:
      - df: DataFrame containing a 'Mark' column.
      - num_clusters: Number of clusters to form.
    
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
        top_terms = [terms[ind] for ind in order_centroids[i, :5]]
        label = " / ".join(top_terms)
        candidate_categories.append(label)
    return candidate_categories

# -----------------------------------------------------------------------------
# Fuzzy Matching for Product Classification
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def classify_mark(mark: str, candidate_categories: list = None, threshold: int = 70) -> str:
    """
    Classify the 'Mark' string into a simplified product category using fuzzy matching.
    
    Parameters:
      - mark (str): The original Mark string.
      - candidate_categories (list): Candidate categories to match against. If None, a default list is used.
      - threshold (int): Minimum matching score required.
    
    Returns:
      A simplified product category or "Other".
    """
    if not isinstance(mark, str):
        return "Unknown"
    if candidate_categories is None:
        candidate_categories = ["Safawi", "Sukkari", "Sugar", "Phoenix", "Unmanufactured"]
    best_match = process.extractOne(mark, candidate_categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

# -----------------------------------------------------------------------------
# Global Data Filters with Cascading (Smart) Filtering
# -----------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame):
    """
    Applies global filters to the DataFrame with real-time, cascading feedback.
    Each filter is presented in a collapsible expander and provides an "All" option.
    The available options for each filter are computed based on the full dataset.
    If no selection is made (or "All" is selected), that dimension is not used to restrict the data.
    
    Returns:
      - The filtered DataFrame.
      - The unit column (fixed as "Tons").
    """
    st.sidebar.header("🔍 Global Data Filters")
    
    # Place the reset button once at the top of the sidebar.
    if st.sidebar.button("Reset Filters", key="unique_reset_filters"):
        st.rerun()

    # A helper function to return the full list if selection is empty or contains "All"
    def ensure_selection(selected, full_list):
        if not selected or "All" in selected:
            return full_list
        return selected

    # Compute full lists for each filter from the full dataset.
    full_states = sorted(df["Consignee State"].dropna().unique().tolist()) if "Consignee State" in df.columns else []
    full_months = sorted(df["Month"].dropna().unique().tolist()) if "Month" in df.columns else []
    full_years = sorted([str(y) for y in df["Year"].dropna().unique().tolist()]) if "Year" in df.columns else []
    full_consignees = sorted(df["Consignee"].dropna().unique().tolist()) if "Consignee" in df.columns else []
    full_exporters = sorted(df["Exporter"].dropna().unique().tolist()) if "Exporter" in df.columns else []
    
    # For product, ensure the "Product" column exists.
    if "Mark" in df.columns and "Product" not in df.columns:
        candidate_categories = generate_candidate_categories(df, num_clusters=5)
        df["Product"] = df["Mark"].apply(lambda x: classify_mark(x, candidate_categories))
    full_products = sorted(df["Product"].dropna().unique().tolist()) if "Product" in df.columns else []

    # --- Filter by Consignee State ---
    with st.sidebar.expander("Filter by Consignee State", expanded=True):
        selected_states = st.multiselect("📌 Select State:", options=["All"] + full_states, default=["All"], key="state_filter")
        selected_states = ensure_selection(selected_states, full_states)

    # --- Filter by Month ---
    with st.sidebar.expander("Filter by Month", expanded=True):
        selected_months = st.multiselect("📅 Select Month:", options=["All"] + full_months, default=["All"], key="month_filter")
        selected_months = ensure_selection(selected_months, full_months)

    # --- Filter by Year ---
    with st.sidebar.expander("Filter by Year", expanded=True):
        selected_years = st.multiselect("📆 Select Year:", options=["All"] + full_years, default=["All"], key="year_filter")
        selected_years = ensure_selection(selected_years, full_years)

    # --- Filter by Consignee ---
    with st.sidebar.expander("Filter by Consignee", expanded=True):
        selected_consignees = st.multiselect("🏢 Select Consignee:", options=["All"] + full_consignees, default=["All"], key="consignee_filter")
        selected_consignees = ensure_selection(selected_consignees, full_consignees)

    # --- Filter by Exporter ---
    with st.sidebar.expander("Filter by Exporter", expanded=True):
        selected_exporters = st.multiselect("🚢 Select Exporter:", options=["All"] + full_exporters, default=["All"], key="exporter_filter")
        selected_exporters = ensure_selection(selected_exporters, full_exporters)

    # --- Filter by Product ---
    with st.sidebar.expander("Filter by Product", expanded=True):
        selected_products = st.multiselect("🔖 Select Product:", options=["All"] + full_products, default=["All"], key="product_filter")
        selected_products = ensure_selection(selected_products, full_products)

    # Build a dictionary of filter criteria.
    filter_criteria = {
        "Consignee State": selected_states,
        "Month": selected_months,
        "Year": selected_years,
        "Consignee": selected_consignees,
        "Exporter": selected_exporters,
        "Product": selected_products,
    }

    # Cascading filtering: apply each filter sequentially.
    filtered_df = df.copy()
    for col, selection in filter_criteria.items():
        if col in df.columns:
            filtered_df = filtered_df[filtered_df[col].isin(selection)]

    # Define the unit column (fixed as "Tons")
    unit_column = "Tons"
    if unit_column in df.columns:
        df[unit_column] = pd.to_numeric(df[unit_column], errors='coerce')

    return filtered_df, unit_column
