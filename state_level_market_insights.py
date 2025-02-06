import streamlit as st
import pandas as pd
import plotly.express as px

def state_level_market_insights(data: pd.DataFrame):
    st.title("🌍 State-Level Market Insights Dashboard")

    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee State", "Tons", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    st.markdown("### 📌 Top Importing States")
    top_states = data.groupby("Consignee State")["Tons"].sum().nlargest(5).reset_index()
    fig1 = px.bar(top_states, x="Consignee State", y="Tons", title="Top Importing States")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 📊 State-Level Growth Tracking")
    state_trends = data.groupby(["Consignee State", "Year"])["Tons"].sum().unstack(fill_value=0)
    st.line_chart(state_trends)
    
    st.success("✅ State-Level Market Insights Loaded Successfully!")
