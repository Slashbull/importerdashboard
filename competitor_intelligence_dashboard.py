import streamlit as st
import pandas as pd
import plotly.express as px

def competitor_intelligence_dashboard(data: pd.DataFrame):
    st.title("🤝 Competitor Intelligence Dashboard")
    
    # Validate required columns.
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure numeric conversion for "Tons".
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create "Period" if not already present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # ---------------------------
    # Compute Competitor KPIs
    # ---------------------------
    # Here, we assume each unique "Consignee" represents a competitor.
    comp_agg = data.groupby("Consignee")["Tons"].sum().reset_index()
    total_volume = comp_agg["Tons"].sum()
    avg_volume = comp_agg["Tons"].mean() if not comp_agg.empty else 0
    
    # Compute period-over-period growth for each competitor.
    growth_list = []
    for comp in comp_agg["Consignee"]:
        comp_data = data[data["Consignee"] == comp].groupby("Period")["Tons"].sum().sort_index()
        if len(comp_data) >= 2 and comp_data.iloc[-2] != 0:
            growth = ((comp_data.iloc[-1] - comp_data.iloc[-2]) / comp_data.iloc[-2]) * 100
            growth_list.append(growth)
        else:
            growth_list.append(0)
    comp_agg["Recent Growth (%)"] = growth_list
    best_growth = comp_agg["Recent Growth (%)"].max() if not comp_agg.empty else 0
    worst_growth = comp_agg["Recent Growth (%)"].min() if not comp_agg.empty else 0

    # ---------------------------
    # Layout: Tabs for Summary, Exporters Breakdown, Growth & Trends
    # ---------------------------
    tab_summary, tab_export, tab_growth = st.tabs(["Summary", "Exporters Breakdown", "Growth & Trends"])
    
    # ----- Summary Tab -----
    with tab_summary:
        st.subheader("Competitor Summary")
        # Display key metrics in columns.
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Competitor Volume (Tons)", f"{total_volume:,.2f}")
        col2.metric("Average Volume per Competitor", f"{avg_volume:,.2f}")
        col3.metric("Best Recent Growth (%)", f"{best_growth:,.2f}")
        col4.metric("Worst Recent Growth (%)", f"{worst_growth:,.2f}")
        
        st.markdown("---")
        st.subheader("Detailed Competitor Summary")
        st.dataframe(comp_agg.sort_values("Tons", ascending=False))
    
    # ----- Exporters Breakdown Tab -----
    with tab_export:
        st.subheader("Exporters Breakdown for Selected Competitor")
        # Display a dropdown of top competitors based on volume.
        candidate_competitors = data.groupby("Consignee")["Tons"].sum().nlargest(10).reset_index()["Consignee"].tolist()
        if candidate_competitors:
            selected_competitor = st.selectbox("Select a Competitor:", candidate_competitors, key="ci_selected_competitor")
            comp_data = data[data["Consignee"] == selected_competitor]
            exporter_breakdown = comp_data.groupby("Exporter")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
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
        else:
            st.info("No competitor data available for exporter breakdown.")
    
    # ----- Growth & Trends Tab -----
    with tab_growth:
        st.subheader("Competitor Trends Over Time")
        # Pivot table for time-series trends.
        trends_df = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(trends_df)
        
        # Detailed growth analysis for a selected competitor.
        candidate_competitors_growth = data.groupby("Consignee")["Tons"].sum().nlargest(10).reset_index()["Consignee"].tolist()
        if candidate_competitors_growth:
            selected_for_growth = st.selectbox("Select Competitor for Detailed Growth Analysis:", candidate_competitors_growth, key="ci_growth")
            comp_trend = data[data["Consignee"] == selected_for_growth].groupby("Period")["Tons"].sum()
            growth_pct = comp_trend.pct_change() * 100
            growth_df = pd.DataFrame({
                "Period": growth_pct.index,
                "Percentage Change (%)": growth_pct.values
            }).reset_index(drop=True)
            st.markdown(f"#### Period-over-Period Growth for {selected_for_growth}")
            st.dataframe(growth_df)
        else:
            st.info("No data available for growth analysis.")
    
    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
