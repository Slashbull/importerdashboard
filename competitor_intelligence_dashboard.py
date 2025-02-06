import streamlit as st
import pandas as pd
import plotly.express as px

def competitor_intelligence_dashboard(data: pd.DataFrame):
    st.title("🤝 Competitor Intelligence Dashboard")

    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    st.markdown("### 🏆 Top Competitors by Import Volume")
    top_competitors = data.groupby("Consignee")["Tons"].sum().nlargest(5).reset_index()
    fig1 = px.bar(top_competitors, x="Consignee", y="Tons", title="Top Competitors")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 🌍 Exporters Used by Top Competitors")
    top_list = top_competitors["Consignee"].tolist()
    filtered = data[data["Consignee"].isin(top_list)]
    competitor_exporters = filtered.groupby(["Consignee", "Exporter"])["Tons"].sum().reset_index()
    st.dataframe(competitor_exporters)
    
    st.markdown("### 📈 Competitor Growth Over Time")
    data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    growth = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
    st.line_chart(growth)
    
    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
