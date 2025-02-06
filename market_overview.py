import streamlit as st
import pandas as pd
import plotly.express as px

def market_overview_dashboard(data: pd.DataFrame):
    st.title("📊 Market Overview Dashboard")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    # Check required columns
    required_columns = ["SR NO.", "Job No.", "Consignee", "Exporter", "Mark", "Tons", "Month", "Year", "Consignee State"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    st.markdown("### 📈 Key Market Insights")
    st.write("**Total Imports (Tons):**", data["Tons"].sum())
    st.write("**Unique Consignees:**", data["Consignee"].nunique())
    st.write("**Unique Exporters:**", data["Exporter"].nunique())

    st.markdown("### 🏆 Top 5 Consignees")
    top_consignees = data.groupby("Consignee")["Tons"].sum().nlargest(5).reset_index()
    fig1 = px.bar(top_consignees, x="Consignee", y="Tons", title="Top 5 Consignees")
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("### 🌍 Top 5 Exporters")
    top_exporters = data.groupby("Exporter")["Tons"].sum().nlargest(5).reset_index()
    fig2 = px.bar(top_exporters, x="Exporter", y="Tons", title="Top 5 Exporters")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("### 📅 Monthly Import Trends")
    monthly_trends = data.groupby("Month")["Tons"].sum().reset_index()
    fig3 = px.line(monthly_trends, x="Month", y="Tons", title="Monthly Import Trends")
    st.plotly_chart(fig3, use_container_width=True)
    
    st.success("✅ Market Overview Dashboard Loaded Successfully!")
