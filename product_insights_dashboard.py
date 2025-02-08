import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from rapidfuzz import process, fuzz

# -------------------------------
# Caching for heavy computations
# -------------------------------
@st.cache_data(show_spinner=False)
def generate_candidate_categories(df: pd.DataFrame, num_clusters: int = 5) -> list:
    """
    Automatically generate candidate product categories from the 'Mark' column.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame.
        num_clusters (int): Number of clusters to form (default 5).
        
    Returns:
        list: A list of candidate product category labels.
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
        # Use the top 5 terms of each cluster to generate a label.
        top_terms = [terms[ind] for ind in order_centroids[i, :5]]
        label = " / ".join(top_terms)
        candidate_categories.append(label)
    return candidate_categories

@st.cache_data(show_spinner=False)
def classify_product(mark: str, candidate_categories: list, threshold: int = 70) -> str:
    """
    Classify a product description (from 'Mark') by fuzzy matching it against candidate categories.
    
    Parameters:
        mark (str): The product description.
        candidate_categories (list): List of candidate category labels.
        threshold (int): Minimum matching score to accept a category (default 70).
        
    Returns:
        str: The selected product category, or "Other" if no match meets the threshold.
    """
    if not isinstance(mark, str) or not candidate_categories:
        return "Unknown"
    
    best_match = process.extractOne(mark, candidate_categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

def product_insights_dashboard(data: pd.DataFrame):
    st.title("📈 Product Insights Dashboard")
    
    # --- Data Validation ---
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Mark", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a "Period" field if not present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Generate candidate product categories using KMeans clustering.
    candidate_categories = generate_candidate_categories(data, num_clusters=5)
    st.sidebar.markdown("**Generated Candidate Categories:**")
    st.sidebar.write(candidate_categories)
    
    # Automatically classify products (if "Product" column is not already present).
    if "Product" not in data.columns:
        data["Product"] = data["Mark"].apply(lambda x: classify_product(x, candidate_categories))
    
    # --- Layout: Create Tabs ---
    tab_overview, tab_trends, tab_market_share, tab_details = st.tabs([
        "Overview", "Trends", "Market Share", "Detailed Analysis"
    ])
    
    # ----- Tab 1: Overview -----
    with tab_overview:
        st.subheader("Key Product Metrics")
        prod_agg = data.groupby("Product")["Tons"].sum().reset_index()
        total_volume = prod_agg["Tons"].sum()
        num_products = prod_agg["Product"].nunique()
        avg_volume = total_volume / num_products if num_products > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Volume (Tons)", f"{total_volume:,.2f}")
        col2.metric("Unique Product Categories", num_products)
        col3.metric("Avg Volume per Category", f"{avg_volume:,.2f}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Top Product Categories")
        top_products = prod_agg.sort_values("Tons", ascending=False).head(5)
        fig_top = px.bar(
            top_products,
            x="Product",
            y="Tons",
            title="Top 5 Product Categories by Volume",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_top, use_container_width=True)
    
    # ----- Tab 2: Trends -----
    with tab_trends:
        st.subheader("Overall Monthly Trends by Product")
        trends_df = data.groupby(["Product", "Period"])["Tons"].sum().reset_index()
        fig_trends = px.line(
            trends_df,
            x="Period",
            y="Tons",
            color="Product",
            title="Monthly Trends by Product Category",
            markers=True
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Detailed Trends for Selected Products")
        all_products = sorted(data["Product"].dropna().unique().tolist())
        # If no selection is made, default to all products.
        selected_products = st.multiselect("Select Product Categories", options=all_products, default=[], key="pi_select")
        if not selected_products:
            selected_products = all_products
        detailed_trends = data[data["Product"].isin(selected_products)]
        detailed_df = detailed_trends.groupby(["Product", "Period"])["Tons"].sum().reset_index()
        fig_detail = px.line(
            detailed_df,
            x="Period",
            y="Tons",
            color="Product",
            title="Detailed Trends for Selected Products",
            markers=True
        )
        st.plotly_chart(fig_detail, use_container_width=True)
    
    # ----- Tab 3: Market Share -----
    with tab_market_share:
        st.subheader("Market Share by Product Category")
        fig_pie = px.pie(
            prod_agg,
            names="Product",
            values="Tons",
            title="Product Category Market Share",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # ----- Tab 4: Detailed Analysis -----
    with tab_details:
        st.subheader("Detailed Product Data")
        pivot_table = data.pivot_table(
            index="Product",
            columns="Period",
            values="Tons",
            aggfunc="sum",
            fill_value=0
        )
        st.dataframe(pivot_table)
        
        st.markdown("#### Summary Table by Product Category")
        summary_table = data.groupby("Product")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        st.dataframe(summary_table)
    
    st.success("✅ Product Insights Dashboard Loaded Successfully!")
