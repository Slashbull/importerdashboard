import streamlit as st
import pandas as pd

# ---- Competitor Intelligence Dashboard ---- #
def competitor_intelligence_dashboard():
    st.title("🤝 Competitor Intelligence Dashboard")

    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    df = st.session_state["uploaded_data"]

    # Ensure required columns exist
    required_columns = ["Consignee", "Exporter", "Kgs"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"🚨 Missing columns in the dataset: {', '.join(missing_columns)}")
        return

    # Convert Kgs to numeric if not already
    df["Kgs"] = pd.to_numeric(df["Kgs"], errors="coerce")

    st.markdown("### 🏆 Top Competitors by Import Volume")
    top_competitors = df.groupby("Consignee")["Kgs"].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_competitors)

    st.markdown("### 🌍 Exporters Used by Top Competitors")
    # Filter data for top competitors
    top_competitors_list = top_competitors.index.tolist()
    filtered_data = df[df["Consignee"].isin(top_competitors_list)]
    competitor_exporters = filtered_data.groupby(["Consignee", "Exporter"])["Kgs"].sum().reset_index()
    st.dataframe(competitor_exporters)

    st.markdown("### 📈 Competitor Growth Over Time")
    if "Month" in df.columns and "Year" in df.columns:
        df["Period"] = df["Month"] + "-" + df["Year"].astype(str)
        growth_trends = df.groupby(["Consignee", "Period"])["Kgs"].sum().unstack(fill_value=0)
        st.line_chart(growth_trends)
    else:
        st.warning("⚠️ Columns 'Month' and 'Year' are required for growth analysis.")

    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
