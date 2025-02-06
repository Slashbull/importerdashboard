import streamlit as st
import pandas as pd
import plotly.express as px

def competitor_intelligence_dashboard(data: pd.DataFrame):
    st.title("🤝 Competitor Intelligence Dashboard")
    
    # Validate data presence and required columns.
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure Tons column is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a "Period" column if not present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Create a tabbed layout.
    tab_top, tab_exporters, tab_growth = st.tabs(["Top Competitors", "Exporters Breakdown", "Growth Analysis"])

    # ---------------------------
    # Tab 1: Top Competitors
    # ---------------------------
    with tab_top:
        st.subheader("Top Competitors by Import Volume")
        # Group by competitor (Consignee) and sum Tons.
        top_competitors = data.groupby("Consignee")["Tons"].sum().nlargest(5).reset_index()
        fig_top = px.bar(
            top_competitors,
            x="Consignee",
            y="Tons",
            title="Top 5 Competitors",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_top, use_container_width=True)

    # ---------------------------
    # Tab 2: Exporters Breakdown
    # ---------------------------
    with tab_exporters:
        st.subheader("Exporters Used by Competitors")
        # Get candidate competitors from the top 10.
        candidate_competitors = (
            data.groupby("Consignee")["Tons"]
            .sum()
            .nlargest(10)
            .reset_index()["Consignee"]
            .tolist()
        )
        selected_competitor = st.selectbox("Select a Competitor:", candidate_competitors)
        filtered_data = data[data["Consignee"] == selected_competitor]
        exporter_breakdown = (
            filtered_data.groupby("Exporter")["Tons"]
            .sum()
            .reset_index()
            .sort_values(by="Tons", ascending=False)
        )
        st.markdown(f"### Exporters for {selected_competitor}")
        fig_exp = px.bar(
            exporter_breakdown,
            x="Exporter",
            y="Tons",
            title=f"Exporters for {selected_competitor}",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_exp, use_container_width=True)
        st.markdown("#### Detailed Exporters Data")
        st.dataframe(exporter_breakdown)

    # ---------------------------
    # Tab 3: Growth Analysis
    # ---------------------------
    with tab_growth:
        st.subheader("Competitor Growth Over Time")
        # Group data by Consignee and Period for a time‑series analysis.
        growth_df = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(growth_df)

        # Additional drill-down: Show period-over-period percentage change for a selected competitor.
        selected_comp = st.selectbox("Select Competitor for Growth Analysis:", candidate_competitors)
        comp_data = data[data["Consignee"] == selected_comp]
        comp_growth = comp_data.groupby("Period")["Tons"].sum().pct_change() * 100
        comp_growth = comp_growth.reset_index()
        comp_growth.columns = ["Period", "Percentage Change (%)"]
        st.markdown(f"#### Growth Percentage Change for {selected_comp}")
        st.dataframe(comp_growth)

    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
