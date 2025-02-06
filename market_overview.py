import streamlit as st
import pandas as pd
import plotly.express as px

def market_overview_dashboard(data: pd.DataFrame):
    st.title("📊 Market Overview Dashboard")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    # Check required columns
    required_columns = ["SR NO.", "Job No.", "Consignee", "Exporter", "Mark", "Kgs", "Tons", "Month", "Year", "Consignee State"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Kgs"] = pd.to_numeric(data["Kgs"], errors="coerce")
    
    st.markdown("### 📈 Key Market Insights")
    st.write("**Total Imports (Kgs):**", data["Kgs"].sum())
    st.write("**Unique Consignees:**", data["Consignee"].nunique())
    st.write("**Unique Exporters:**", data["Exporter"].nunique())

    st.markdown("### 🏆 Top 5 Consignees")
    top_consignees = data.groupby("Consignee")["Kgs"].sum().nlargest(5).reset_index()
    fig1 = px.bar(top_consignees, x="Consignee", y="Kgs", title="Top 5 Consignees")
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("### 🌍 Top 5 Exporters")
    top_exporters = data.groupby("Exporter")["Kgs"].sum().nlargest(5).reset_index()
    fig2 = px.bar(top_exporters, x="Exporter", y="Kgs", title="Top 5 Exporters")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("### 📅 Monthly Import Trends")
    monthly_trends = data.groupby("Month")["Kgs"].sum().reset_index()
    fig3 = px.line(monthly_trends, x="Month", y="Kgs", title="Monthly Import Trends")
    st.plotly_chart(fig3, use_container_width=True)
    
    st.success("✅ Market Overview Dashboard Loaded Successfully!")
