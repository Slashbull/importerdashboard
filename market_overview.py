import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Market Overview Dashboard ---- #
def market_overview_dashboard(df):
    """Displays market trends and key insights."""
    st.title("📊 Market Overview Dashboard")

    st.markdown("""
    The Market Overview Dashboard provides a comprehensive view of import trends, competitor insights, 
    supplier performance, and state-wise analysis to help make informed decisions.
    """)

    if df is None or df.empty:
        st.warning("⚠️ No data available. Please upload a dataset in the core system.")
        return

    # ---- Key Metrics ---- #
    total_imports = pd.to_numeric(df["Quanity (Kgs)"], errors='coerce').sum() if "Quanity (Kgs)" in df.columns else 0
    unique_suppliers = df["Exporter"].nunique() if "Exporter" in df.columns else 0
    unique_competitors = df["Consignee"].nunique() if "Consignee" in df.columns else 0
    top_state = df.groupby("Consignee State")["Quanity (Kgs)"].sum().idxmax() if "Consignee State" in df.columns else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Import Volume (Kgs)", f"{total_imports:,.2f}" if isinstance(total_imports, (int, float)) else "N/A")
    col2.metric("🏭 Unique Suppliers", unique_suppliers)
    col3.metric("🏆 Unique Competitors", unique_competitors)
    col4.metric("📍 Top State by Volume", top_state)

    # ---- Monthly Trend Analysis ---- #
    if "Month" in df.columns and "Quanity (Kgs)" in df.columns:
        st.subheader("📅 Monthly Import Trends")
        monthly_trends = df.groupby("Month")["Quanity (Kgs)"].sum().reset_index()
        fig = px.line(monthly_trends, x="Month", y="Quanity (Kgs)", title="Monthly Import Trends")
        st.plotly_chart(fig, use_container_width=True)

    # ---- Top 5 Competitors ---- #
    if "Consignee" in df.columns and "Quanity (Kgs)" in df.columns:
        st.subheader("🏆 Top 5 Importing Competitors")
        top_competitors = df.groupby("Consignee")["Quanity (Kgs)"].sum().reset_index()
    top_competitors = top_competitors.nlargest(5, "Quanity (Kgs)", "all")
        fig = px.bar(top_competitors, x="Consignee", y="Quanity (Kgs)", title="Top 5 Importing Competitors")
        st.plotly_chart(fig, use_container_width=True)

    # ---- Top 5 Suppliers ---- #
    if "Exporter" in df.columns and "Quanity (Kgs)" in df.columns:
        st.subheader("🏭 Top 5 Suppliers by Import Volume")
        top_suppliers = df.groupby("Exporter")["Quanity (Kgs)"].sum().reset_index()
    top_suppliers = top_suppliers.nlargest(5, "Quanity (Kgs)", "all")
        fig = px.bar(top_suppliers, x="Exporter", y="Quanity (Kgs)", title="Top 5 Suppliers")
        st.plotly_chart(fig, use_container_width=True)

    # ---- State-Wise Analysis ---- #
    if "Consignee State" in df.columns and "Quanity (Kgs)" in df.columns:
        st.subheader("📍 State-Wise Import Trends")
        state_imports = df.groupby("Consignee State")["Quanity (Kgs)"].sum().reset_index()
        fig = px.choropleth(
            state_imports,
            locations="Consignee State",
            locationmode="country names",
            color="Quanity (Kgs)",
            title="State-Wise Import Trends",
        )
        st.plotly_chart(fig, use_container_width=True)

# Save file as market_overview.py
