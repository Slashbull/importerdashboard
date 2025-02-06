import streamlit as st
import pandas as pd
import plotly.express as px

def classify_mark(mark: str) -> str:
    """
    A simple classifier that extracts a product category from a long mark string.
    The function checks for key terms and returns a simplified category.
    """
    if not isinstance(mark, str):
        return "Unknown"
    mark_lower = mark.lower()
    # Check for keywords in a prioritized order
    if "safawi" in mark_lower:
        return "Safawi"
    if "sukkari" in mark_lower:
        return "Sukkari"
    if "sugar" in mark_lower:
        return "Sugar"
    if "phoenix" in mark_lower:
        return "Phoenix"
    if "unmanufactured" in mark_lower:
        return "Unmanufactured"
    # Add other keywords as needed...
    return "Other"

def competitor_intelligence_dashboard(data: pd.DataFrame):
    st.title("🤝 Competitor Intelligence Dashboard")
    
    # Check that required data exists
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    # Required columns include "Mark" for product classification
    required_columns = ["Consignee", "Exporter", "Mark", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure the Tons column is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Create a new column 'Product' by classifying the long text in "Mark"
    data["Product"] = data["Mark"].apply(classify_mark)

    # --- Product Filter ---
    # Allow the user to select a product category for analysis.
    product_options = sorted(data["Product"].dropna().unique().tolist())
    product_options = ["All"] + product_options
    selected_product = st.selectbox("Filter by Product", options=product_options, index=0)
    if selected_product != "All":
        data = data[data["Product"] == selected_product]
    
    # Create tabs for different sections of the dashboard
    tab_top, tab_exporters, tab_growth = st.tabs([
        "Top Competitors", "Exporters Used", "Growth Analysis"
    ])
    
    # ---------------------------
    # Tab 1: Top Competitors by Import Volume
    # ---------------------------
    with tab_top:
        st.subheader("Top Competitors by Import Volume")
        # Let the user choose the number of top competitors to display
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
    
    # ---------------------------
    # Tab 2: Exporters Used by Top Competitors
    # ---------------------------
    with tab_exporters:
        st.subheader("Exporters Breakdown for a Selected Competitor")
        # Build a candidate list from the top 10 competitors (based on Tons)
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
        st.dataframe(exporter_breakdown)
        fig_exporters = px.bar(
            exporter_breakdown,
            x="Exporter",
            y="Tons",
            title=f"Exporters for {selected_competitor}",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig_exporters, use_container_width=True)
    
    # ---------------------------
    # Tab 3: Competitor Growth Analysis
    # ---------------------------
    with tab_growth:
        st.subheader("Competitor Growth Over Time")
        # Create a "Period" column by concatenating Month and Year
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
        # Group data by Consignee and Period
        growth_df = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(growth_df)
        
        # Calculate period-over-period percentage changes
        pct_change_df = growth_df.pct_change(axis=1) * 100
        pct_change_df = pct_change_df.round(2)
        st.markdown("#### Period-over-Period Percentage Change (%)")
        st.dataframe(pct_change_df)
    
    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
