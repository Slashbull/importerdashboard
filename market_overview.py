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
    total_imports = df["Quanity (Kgs)"].sum()
    unique_suppliers = df["Exporter"].nunique()
    unique_competitors = df["Consignee"].nunique()
    top_state = df.groupby("Consignee State")["Quanity (Kgs)"].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Import Volume (Kgs)", f"{total_imports:,.2f}")
    col2.metric("🏭 Unique Suppliers", unique_suppliers)
    col3.metric("🏆 Unique Competitors", unique_competitors)
    col4.metric("📍 Top State by Volume", top_state)

    # ---- Monthly Trend Analysis ---- #
    st.subheader("📅 Monthly Import Trends")
    monthly_trends = df.groupby("Month")["Quanity (Kgs)"].sum().reset_index()
    fig = px.line(monthly_trends, x="Month", y="Quanity (Kgs)", title="Monthly Import Trends")
    st.plotly_chart(fig, use_container_width=True)

    # ---- Top 5 Competitors ---- #
    st.subheader("🏆 Top 5 Importing Competitors")
    top_competitors = df.groupby("Consignee")["Quanity (Kgs)"].sum().nlargest(5).reset_index()
    fig = px.bar(top_competitors, x="Consignee", y="Quanity (Kgs)", title="Top 5 Importing Competitors")
    st.plotly_chart(fig, use_container_width=True)

    # ---- Top 5 Suppliers ---- #
    st.subheader("🏭 Top 5 Suppliers by Import Volume")
    top_suppliers = df.groupby("Exporter")["Quanity (Kgs)"].sum().nlargest(5).reset_index()
    fig = px.bar(top_suppliers, x="Exporter", y="Quanity (Kgs)", title="Top 5 Suppliers")
    st.plotly_chart(fig, use_container_width=True)

    # ---- State-Wise Analysis ---- #
    st.subheader("📍 State-Wise Import Trends")
    state_imports = df.groupby("Consignee State")["Quanity (Kgs)"].sum().reset_index()
    fig = px.choropleth(
        state_imports,
        locations="Consignee State",
        locationmode="USA-states",
        color="Quanity (Kgs)",
        title="State-Wise Import Trends",
    )
    st.plotly_chart(fig, use_container_width=True)

# Save file as market_overview.py
