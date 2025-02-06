import streamlit as st
import pandas as pd

# ---- State-Level Market Insights Dashboard ---- #
def state_level_market_insights():
    st.title("🌍 State-Level Market Insights Dashboard")

    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    df = st.session_state["uploaded_data"]

    # Ensure required columns exist
    required_columns = ["Consignee State", "Kgs"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"🚨 Missing columns in the dataset: {', '.join(missing_columns)}")
        return

    # Convert Kgs to numeric if not already
    df["Kgs"] = pd.to_numeric(df["Kgs"], errors="coerce")

    st.markdown("### 📌 Top Importing States")
    top_states = df.groupby("Consignee State")["Kgs"].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_states)

    st.markdown("### 📊 State-Level Growth Tracking (3-Year Trends)")
    if "Year" in df.columns:
        state_trends = df.groupby(["Consignee State", "Year"])["Kgs"].sum().unstack(fill_value=0)
        st.line_chart(state_trends)
    else:
        st.warning("⚠️ Column 'Year' is required for tracking trends.")
    
    st.success("✅ State-Level Market Insights Loaded Successfully!")
