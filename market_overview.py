import streamlit as st
import pandas as pd
import plotly.express as px

def competitor_intelligence_dashboard(data: pd.DataFrame):
    st.title("🤝 Competitor Intelligence Dashboard")
    
    # Validate that required columns exist
    required_columns = ["Consignee", "Exporter", "Mark", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return
    if data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    # Ensure Tons is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a Period column if not already present (for time-series analysis)
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Layout: Two main tabs – Overview and Detailed Trends
    tab_overview, tab_trends = st.tabs(["Overview", "Detailed Trends"])
    
    # ---------------------------
    # Tab 1: Overview
    # ---------------------------
    with tab_overview:
        st.subheader("Top Competitors Overview")
        # Compute top competitors by total Tons (grouped by Consignee)
        top_competitors = data.groupby("Consignee")["Tons"].sum().nlargest(5).reset_index()
        fig_bar = px.bar(
            top_competitors,
            x="Consignee",
            y="Tons",
            title="Top 5 Competitors by Tons",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Hierarchical Contribution (Sunburst)")
        st.markdown("The sunburst chart below shows the hierarchical breakdown by competitor (Consignee) and product category (derived from Mark).")
        # For a hierarchical view, we use a sunburst chart.
        # We'll use 'Consignee' as the parent and 'Exporter' as the child level.
        # (Optionally, if your filters have created a 'Product' column, you could add that as an additional level.)
        fig_sun = px.sunburst(
            data,
            path=["Consignee", "Exporter"],
            values="Tons",
            title="Sunburst: Competitor → Exporter",
            color="Tons",
            color_continuous_scale="Blues",
            hover_data={"Tons": True}
        )
        st.plotly_chart(fig_sun, use_container_width=True)
    
    # ---------------------------
    # Tab 2: Detailed Trends
    # ---------------------------
    with tab_trends:
        st.subheader("Competitor Performance Over Time")
        # Create a pivot table of Tons by Consignee and Period
        trends_df = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(trends_df)
        
        st.markdown("---")
        st.subheader("Period-over-Period Percentage Change")
        # Calculate the percentage change along the period axis for each competitor
        pct_change_df = trends_df.pct_change(axis=1) * 100
        pct_change_df = pct_change_df.round(2)
        st.dataframe(pct_change_df)
    
    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
