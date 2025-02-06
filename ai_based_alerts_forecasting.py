import streamlit as st
import pandas as pd

# ---- AI-Based Alerts & Forecasting Dashboard ---- #
def ai_based_alerts_forecasting():
    st.title("🔮 AI-Based Alerts & Forecasting Dashboard")

    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    df = st.session_state["uploaded_data"]

    # Ensure required columns exist
    required_columns = ["Consignee", "Exporter", "Kgs", "Month", "Year"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"🚨 Missing columns in the dataset: {', '.join(missing_columns)}")
        return

    # Convert Kgs to numeric if not already
    df["Kgs"] = pd.to_numeric(df["Kgs"], errors="coerce")

    st.markdown("### 🚨 Competitor Growth Alerts")
    competitor_growth = df.groupby("Consignee")["Kgs"].sum().pct_change().dropna()
    high_growth_competitors = competitor_growth[competitor_growth > 0.2]
    if not high_growth_competitors.empty:
        st.write("#### Competitors with Rapid Growth:")
        st.dataframe(high_growth_competitors)
    else:
        st.success("✅ No significant competitor growth detected.")

    st.markdown("### ⚠️ Supplier Risk Warnings")
    supplier_risk = df.groupby("Exporter")["Kgs"].sum().pct_change().dropna()
    risky_suppliers = supplier_risk[supplier_risk < -0.2]
    if not risky_suppliers.empty:
        st.write("#### Suppliers with Major Decline:")
        st.dataframe(risky_suppliers)
    else:
        st.success("✅ No supplier risks detected.")

    st.markdown("### 🔮 Predicted Next Quarter Growth")
    if "Year" in df.columns and "Month" in df.columns:
        df["Period"] = df["Month"] + "-" + df["Year"].astype(str)
        forecast_trend = df.groupby("Period")["Kgs"].sum().rolling(window=3).mean().dropna()
        st.line_chart(forecast_trend)
    else:
        st.warning("⚠️ Columns 'Month' and 'Year' are required for forecasting.")

    st.success("✅ AI-Based Alerts & Forecasting Dashboard Loaded Successfully!")
