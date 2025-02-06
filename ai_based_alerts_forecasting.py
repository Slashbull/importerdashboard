import streamlit as st
import pandas as pd
import plotly.express as px

def ai_based_alerts_forecasting(data: pd.DataFrame):
    st.title("🔮 AI-Based Alerts & Forecasting Dashboard")

    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    st.markdown("### 🚨 Competitor Growth Alerts")
    competitor_growth = data.groupby("Consignee")["Tons"].sum().pct_change().dropna()
    high_growth = competitor_growth[competitor_growth > 0.2]
    if not high_growth.empty:
        st.write("#### Competitors with Rapid Growth:")
        st.dataframe(high_growth.reset_index())
    else:
        st.success("✅ No significant competitor growth detected.")

    st.markdown("### ⚠️ Supplier Risk Warnings")
    supplier_risk = data.groupby("Exporter")["Tons"].sum().pct_change().dropna()
    risky_suppliers = supplier_risk[supplier_risk < -0.2]
    if not risky_suppliers.empty:
        st.write("#### Suppliers with Major Decline:")
        st.dataframe(risky_suppliers.reset_index())
    else:
        st.success("✅ No supplier risks detected.")

    st.markdown("### 🔮 Forecasting Next Quarter Growth")
    data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    forecast = data.groupby("Period")["Tons"].sum().rolling(window=3).mean().dropna().reset_index()
    fig = px.line(forecast, x="Period", y="Tons", title="Forecasting Trend (Rolling Mean)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("✅ AI-Based Alerts & Forecasting Dashboard Loaded Successfully!")
