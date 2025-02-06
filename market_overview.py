import streamlit as st
import pandas as pd

# ---- Market Overview Dashboard ---- #
def market_overview_dashboard(df):
    """Displays market trends and key insights."""
    st.title("📊 Market Overview")
    st.markdown("""
    This dashboard provides a high-level snapshot of import trends, key competitors, 
    supplier performance, and market dynamics.
    """)
    
    if df is None or df.empty:
        st.warning("⚠️ No data available. Please upload a dataset in the core system.")
        return
    
    # ---- Key Metrics ---- #
    total_imports = df["Quanity (Kgs)"].sum()
    unique_suppliers = df["Exporter"].nunique()
    unique_competitors = df["Consignee"].nunique()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Import Volume (Kgs)", f"{total_imports:,.2f}")
    col2.metric("🏭 Unique Suppliers", unique_suppliers)
    col3.metric("🏆 Unique Competitors", unique_competitors)
    
    # ---- Monthly Trend Analysis ---- #
    st.subheader("📅 Monthly Import Trends")
    monthly_trend = df.groupby("Month")["Quanity (Kgs)"].sum().reset_index()
    st.line_chart(monthly_trend, x="Month", y="Quanity (Kgs)")
    
    # ---- Top 5 Competitors ---- #
    st.subheader("🏆 Top 5 Importing Competitors")
    top_competitors = df.groupby("Consignee")["Quanity (Kgs)"].sum().nlargest(5).reset_index()
    st.bar_chart(top_competitors, x="Consignee", y="Quanity (Kgs)")
    
    # ---- Top 5 Suppliers ---- #
    st.subheader("🏭 Top 5 Suppliers by Import Volume")
    top_suppliers = df.groupby("Exporter")["Quanity (Kgs)"].sum().nlargest(5).reset_index()
    st.bar_chart(top_suppliers, x="Exporter", y="Quanity (Kgs)")
    
    # ---- State-Wise Import Trends ---- #
    st.subheader("📍 State-Wise Import Trends")
    state_imports = df.groupby("Consignee State")["Quanity (Kgs)"].sum().reset_index()
    st.map(state_imports)

# Save file as market_overview.py
