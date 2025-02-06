import streamlit as st
import pandas as pd

def market_overview_dashboard():
    st.title("📊 Market Overview Dashboard")
    
    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return
    
    df = st.session_state["uploaded_data"]

    # Ensure required columns exist
    required_columns = ["SR NO.", "Job No.", "Consignee", "Exporter", "Mark", "Kgs", "Tons", "Month", "Year", "Consignee State"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"🚨 Missing columns in the dataset: {', '.join(missing_columns)}")
        return

    df["Kgs"] = pd.to_numeric(df["Kgs"], errors="coerce")

    st.markdown("### 📈 Key Market Insights")
    st.write("#### Total Imports (Kgs):", df["Kgs"].sum())
    st.write("#### Number of Unique Consignees:", df["Consignee"].nunique())
    st.write("#### Number of Unique Exporters:", df["Exporter"].nunique())
    
    st.markdown("### 🏆 Top 5 Consignees")
    top_consignees = df.groupby("Consignee")["Kgs"].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_consignees)
    
    st.markdown("### 🌍 Top 5 Exporters")
    top_exporters = df.groupby("Exporter")["Kgs"].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_exporters)
    
    st.markdown("### 📅 Monthly Import Trends")
    monthly_trends = df.groupby("Month")["Kgs"].sum()
    st.line_chart(monthly_trends)
    
    st.success("✅ Market Overview Dashboard Loaded Successfully!")
