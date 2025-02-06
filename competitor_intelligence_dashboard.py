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

    # Ensure that Tons is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a 'Period' column if not present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)

    # Define a tabbed layout.
    tab_top, tab_exporters, tab_growth = st.tabs(["Top Competitors", "Exporters Breakdown", "Growth & Trends"])

    # ---------------------------
    # Tab 1: Top Competitors
    # ---------------------------
    with tab_top:
        st.subheader("Top Competitors by Import Volume")
        # Let the user choose the number of top competitors to display.
        top_n = st.selectbox(
            "Select number of top competitors to display:",
            options=[5, 10, 15, 20, 25],
            index=0
        )
        top_competitors = (
            data.groupby("Consignee")["Tons"]
            .sum()
            .nlargest(top_n)
            .reset_index()
        )
        fig_top = px.bar(
            top_competitors,
            x="Consignee",
            y="Tons",
            title=f"Top {top_n} Competitors by Tons",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_top, use_container_width=True)

    # ---------------------------
    # Tab 2: Exporters Breakdown
    # ---------------------------
    with tab_exporters:
        st.subheader("Exporters Breakdown for Selected Competitor")
        # Create a candidate list: top 10 competitors by volume.
        candidate_competitors = (
            data.groupby("Consignee")["Tons"]
            .sum()
            .nlargest(10)
            .reset_index()["Consignee"]
            .tolist()
        )
        selected_competitor = st.selectbox("Select a Competitor:", candidate_competitors)
        comp_data = data[data["Consignee"] == selected_competitor]
        exporter_breakdown = (
            comp_data.groupby("Exporter")["Tons"]
            .sum()
            .reset_index()
            .sort_values(by="Tons", ascending=False)
        )
        st.markdown(f"### Exporters for {selected_competitor}")
        fig_export = px.bar(
            exporter_breakdown,
            x="Exporter",
            y="Tons",
            title=f"Exporters for {selected_competitor}",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_export, use_container_width=True)
        st.markdown("#### Detailed Exporters Data")
        st.dataframe(exporter_breakdown)

    # ---------------------------
    # Tab 3: Growth & Trends
    # ---------------------------
    with tab_growth:
        st.subheader("Competitor Trends Over Time")
        trends_df = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(trends_df)
        
        # Additional drill-down: Select a competitor for detailed growth analysis.
        candidate_competitors_growth = (
            data.groupby("Consignee")["Tons"]
            .sum()
            .nlargest(10)
            .reset_index()["Consignee"]
            .tolist()
        )
        selected_for_growth = st.selectbox("Select Competitor for Detailed Growth Analysis:", candidate_competitors_growth)
        comp_trend = data[data["Consignee"] == selected_for_growth].groupby("Period")["Tons"].sum()
        growth_pct = comp_trend.pct_change() * 100
        growth_df = pd.DataFrame({
            "Period": growth_pct.index,
            "Percentage Change (%)": growth_pct.values
        }).reset_index(drop=True)
        st.markdown(f"#### Period-over-Period Growth for {selected_for_growth}")
        st.dataframe(growth_df)

    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
