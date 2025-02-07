import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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

    # Ensure 'Tons' is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a "Period" field if not already present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # ---------------------------
    # Compute Competitor Summary Metrics
    # ---------------------------
    # We assume each unique "Consignee" represents a competitor.
    comp_summary = data.groupby("Consignee")["Tons"].sum().reset_index()
    total_comp_volume = comp_summary["Tons"].sum()
    avg_volume = comp_summary["Tons"].mean() if not comp_summary.empty else 0

    # Compute recent period-over-period growth for each competitor.
    growth_list = []
    for comp in comp_summary["Consignee"]:
        comp_data = data[data["Consignee"] == comp].groupby("Period")["Tons"].sum().sort_index()
        if len(comp_data) >= 2 and comp_data.iloc[-2] != 0:
            growth = ((comp_data.iloc[-1] - comp_data.iloc[-2]) / comp_data.iloc[-2]) * 100
            growth_list.append(growth)
        else:
            growth_list.append(0)
    comp_summary["Recent Growth (%)"] = growth_list
    best_growth = comp_summary["Recent Growth (%)"].max() if not comp_summary.empty else 0
    worst_growth = comp_summary["Recent Growth (%)"].min() if not comp_summary.empty else 0

    # ---------------------------
    # Layout: Four Tabs
    # ---------------------------
    tab_summary, tab_export, tab_trends, tab_detailed = st.tabs([
        "Summary", "Exporters Breakdown", "Trends & Growth", "Detailed Analysis"
    ])
    
    # ----- Tab 1: Summary -----
    with tab_summary:
        st.subheader("Competitor Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Competitor Volume (Tons)", f"{total_comp_volume:,.2f}")
        col2.metric("Average Volume per Competitor", f"{avg_volume:,.2f}")
        col3.metric("Best Recent Growth (%)", f"{best_growth:,.2f}")
        col4.metric("Worst Recent Growth (%)", f"{worst_growth:,.2f}")
        
        st.markdown("---")
        st.subheader("Detailed Competitor Summary")
        st.dataframe(comp_summary.sort_values("Tons", ascending=False))
    
    # ----- Tab 2: Exporters Breakdown -----
    with tab_export:
        st.subheader("Exporters Breakdown for Selected Competitor")
        # Toggle: Show only top 10 competitors or all.
        show_top_exporters = st.checkbox("Show only top 10 competitors", value=True, key="show_top_exporters")
        if show_top_exporters:
            candidate_competitors = data.groupby("Consignee")["Tons"].sum().nlargest(10).reset_index()["Consignee"].tolist()
        else:
            candidate_competitors = sorted(data["Consignee"].dropna().unique().tolist())
            
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
    
    # ----- Tab 3: Trends & Growth -----
    with tab_trends:
        st.subheader("Competitor Trends Over Time")
        trends_df = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(trends_df)
        
        st.markdown("---")
        st.subheader("Detailed Growth Analysis")
        # Toggle: Show only top 10 competitors or all.
        show_top_growth = st.checkbox("Show only top 10 competitors", value=True, key="show_top_growth")
        if show_top_growth:
            candidate_for_growth = data.groupby("Consignee")["Tons"].sum().nlargest(10).reset_index()["Consignee"].tolist()
        else:
            candidate_for_growth = sorted(data["Consignee"].dropna().unique().tolist())
            
        if candidate_for_growth:
            selected_for_growth = st.selectbox("Select Competitor for Growth Analysis:", candidate_for_growth, key="ci_growth")
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
    
    # ----- Tab 4: Detailed Analysis -----
    with tab_detailed:
        st.subheader("Detailed Competitor Analysis")
        st.markdown("Select one or more competitors to compare detailed metrics and trends.")
        # Default to selecting all competitors.
        all_competitors = sorted(data["Consignee"].dropna().unique().tolist())
        selected_comps = st.multiselect("Select Competitors:", all_competitors, default=all_competitors, key="ci_detailed")
        if selected_comps:
            detailed_data = data[data["Consignee"].isin(selected_comps)]
            # Combined line chart comparing trends.
            trends_comp = detailed_data.groupby(["Consignee", "Period"])["Tons"].sum().reset_index()
            fig_compare = px.line(
                trends_comp,
                x="Period",
                y="Tons",
                color="Consignee",
                title="Competitor Comparison Over Time",
                markers=True
            )
            st.plotly_chart(fig_compare, use_container_width=True)
            # Create a pivot table with row totals and a total row.
            pivot_table = detailed_data.pivot_table(
                index="Consignee",
                columns="Period",
                values="Tons",
                aggfunc="sum",
                fill_value=0
            )
            pivot_table["Total"] = pivot_table.sum(axis=1)
            total_row = pd.DataFrame(pivot_table.sum(axis=0)).T
            total_row.index = ["Total"]
            pivot_table_with_total = pd.concat([pivot_table, total_row])
            st.markdown("#### Detailed Volume Pivot Table (with Totals)")
            st.dataframe(pivot_table_with_total)
        else:
            st.info("Please select at least one competitor for detailed analysis.")
    
    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
