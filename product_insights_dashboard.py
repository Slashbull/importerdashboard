import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from rapidfuzz import process, fuzz

# ----------------------------------
# Function to generate candidate categories automatically
# ----------------------------------
@st.cache_data(show_spinner=False)
def generate_candidate_categories(df: pd.DataFrame, num_clusters: int = 5) -> list:
    """
    Automatically generate candidate product categories from the 'Mark' column.
    
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
        top_terms = [terms[ind] for ind in order_centroids[i, :5]]
        label = " / ".join(top_terms)
        candidate_categories.append(label)
    return candidate_categories

# ----------------------------------
# Function to classify product using fuzzy matching
# ----------------------------------
@st.cache_data(show_spinner=False)
def classify_product(mark: str, candidate_categories: list, threshold: int = 70) -> str:
    """
    Classify a product description (from 'Mark') by fuzzy matching it against candidate categories.
    
    Parameters:
      - mark (str): The product description.
      - candidate_categories (list): List of candidate category labels.
      - threshold (int): Minimum matching score to accept a category.
    
    Returns:
      A simplified product category, or "Other" if no match meets the threshold.
    """
    if not isinstance(mark, str) or not candidate_categories:
        return "Unknown"
    best_match = process.extractOne(mark, candidate_categories, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return "Other"

# ----------------------------------
# Main Dashboard Function: Product Insights Dashboard
# ----------------------------------
def product_insights_dashboard(data: pd.DataFrame):
    st.title("📈 Product Insights Dashboard")
    
    # ---------------------------
    # Data Validation & Preprocessing
    # ---------------------------
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Mark", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Generate candidate product categories automatically
    candidate_categories = generate_candidate_categories(data, num_clusters=5)
    st.sidebar.markdown("**Generated Candidate Categories:**")
    st.sidebar.write(candidate_categories)
    
    # Create the Product column using fuzzy matching
    if "Product" not in data.columns:
        data["Product"] = data["Mark"].apply(lambda x: classify_product(x, candidate_categories))

    # ---------------------------
    # Tabbed Layout: Overview, Trends, Market Share, Detailed Analysis
    # ---------------------------
    tab_overview, tab_trends, tab_market_share, tab_details = st.tabs(
        ["Overview", "Trends", "Market Share", "Detailed Analysis"]
    )

    # ---------------------------
    # Tab 1: Overview – KPIs & Top Product Categories
    # ---------------------------
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
        top_products = prod_agg.sort_values(by="Tons", ascending=False).head(5)
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

    # ---------------------------
    # Tab 2: Trends – Time Series Analysis by Product
    # ---------------------------
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
        selected_products = st.multiselect("Select Product Categories", options=all_products, default=all_products[:3])
        if selected_products:
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
        else:
            st.info("Please select at least one product category for detailed analysis.")

    # ---------------------------
    # Tab 3: Market Share – Distribution by Product
    # ---------------------------
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

    # ---------------------------
    # Tab 4: Detailed Analysis – Pivot Table & Summary
    # ---------------------------
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
