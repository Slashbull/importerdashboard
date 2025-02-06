import streamlit as st
import pandas as pd
import plotly.express as px

def competitor_intelligence_dashboard(data: pd.DataFrame):
    st.title("🤝 Competitor Intelligence Dashboard")
    
    # Check required data and columns
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure the Tons column is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Create a tabbed layout for the dashboard
    tab_top, tab_exporters, tab_growth = st.tabs([
        "Top Competitors", "Exporters Used", "Growth Analysis"
    ])
    
    # ===============================
    # Tab 1: Top Competitors by Import Volume
    # ===============================
    with tab_top:
        st.subheader("Top Competitors by Import Volume")
        # Let the user choose how many top competitors to display
        top_n = st.selectbox("Select number of top competitors:", options=[5, 10, 15], index=0)
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
            text_auto=True
        )
        st.plotly_chart(fig_top, use_container_width=True)
    
    # ===============================
    # Tab 2: Exporters Used by Top Competitors
    # ===============================
    with tab_exporters:
        st.subheader("Exporters Breakdown for a Selected Competitor")
        # For the purpose of this tab, let the user choose one competitor from the top competitors list.
        # We'll use the top 10 competitors as the candidate list.
        candidate_competitors = (
            data.groupby("Consignee")["Tons"].sum()
            .nlargest(10)
            .reset_index()["Consignee"]
            .tolist()
        )
        selected_competitor = st.selectbox("Select a Competitor:", candidate_competitors)
        # Filter data for the selected competitor
        comp_data = data[data["Consignee"] == selected_competitor]
        # Group by Exporter and sum the Tons
        exporter_breakdown = (
            comp_data.groupby("Exporter")["Tons"]
            .sum()
            .reset_index()
            .sort_values(by="Tons", ascending=False)
        )
        st.dataframe(exporter_breakdown)
        # Optionally, display a stacked bar chart if there are multiple exporters per competitor
        fig_exporters = px.bar(
            exporter_breakdown,
            x="Exporter",
            y="Tons",
            title=f"Exporters for {selected_competitor}",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig_exporters, use_container_width=True)
    
    # ===============================
    # Tab 3: Competitor Growth Analysis
    # ===============================
    with tab_growth:
        st.subheader("Competitor Growth Over Time")
        # Create a Period column by combining Month and Year
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
        
        # Group data by Consignee and Period
        growth_df = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        
        # Display the time-series line chart for all competitors
        st.line_chart(growth_df)
        
        # Calculate period-over-period percentage change for each competitor
        pct_change_df = growth_df.pct_change(axis=1) * 100
        pct_change_df = pct_change_df.round(2)
        
        st.markdown("#### Period-over-Period Percentage Change (%)")
        st.dataframe(pct_change_df)
    
    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
