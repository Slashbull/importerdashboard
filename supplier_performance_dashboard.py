import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def supplier_performance_dashboard(data: pd.DataFrame):
    st.title("📊 Supplier Performance Dashboard")
    
    # ---------------------------
    # Data & Column Validation
    # ---------------------------
    required_columns = ["Exporter", "Consignee", "Tons", "Month", "Year"]
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert Tons to numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a "Period" column (Month-Year) if not already present
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Define a month ordering dictionary (for potential trends analysis)
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    # ---------------------------
    # Tabbed Layout
    # ---------------------------
    tab_kpis, tab_top, tab_trends, tab_importers = st.tabs([
        "Key Metrics", "Top Suppliers", "Trends & Risk Analysis", "Importer Connections"
    ])

    # ---------------------------
    # Tab 1: Key Metrics
    # ---------------------------
    with tab_kpis:
        st.subheader("Supplier Key Performance Indicators")
        # Aggregate supplier volume
        supplier_agg = data.groupby("Exporter")["Tons"].sum().reset_index()
        total_volume = supplier_agg["Tons"].sum()
        num_suppliers = supplier_agg["Exporter"].nunique()
        avg_volume = total_volume / num_suppliers if num_suppliers > 0 else 0

        # Calculate risk metrics: for each supplier, compute standard deviation and coefficient of variation (CV)
        risk_stats = data.groupby("Exporter")["Tons"].agg(["mean", "std"]).reset_index()
        risk_stats["CV (%)"] = np.where(risk_stats["mean"] > 0, (risk_stats["std"] / risk_stats["mean"]) * 100, 0)
        avg_std = risk_stats["std"].mean() if not risk_stats.empty else 0
        avg_cv = risk_stats["CV (%)"].mean() if not risk_stats.empty else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Volume (Tons)", f"{total_volume:,.2f}")
        col2.metric("Unique Suppliers", num_suppliers)
        col3.metric("Avg Volume per Supplier", f"{avg_volume:,.2f}")
        col4.metric("Avg Std Dev (Tons)", f"{avg_std:,.2f}")
        col5.metric("Avg CV (%)", f"{avg_cv:,.2f}")

    # ---------------------------
    # Tab 2: Top Suppliers
    # ---------------------------
    with tab_top:
        st.subheader("Top Suppliers by Volume")
        top_n = st.selectbox("Select number of top suppliers to display:", options=[5, 10, 15, 20, 25], index=0)
        top_suppliers = supplier_agg.nlargest(top_n, "Tons")
        fig_top = px.bar(
            top_suppliers,
            x="Exporter",
            y="Tons",
            title=f"Top {top_n} Suppliers by Volume",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_top, use_container_width=True)

    # ---------------------------
    # Tab 3: Trends & Risk Analysis
    # ---------------------------
    with tab_trends:
        st.subheader("Supplier Performance Trends")
        # Pivot the data to create a time-series view: rows = Exporter, columns = Period
        trends_df = data.groupby(["Exporter", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(trends_df)
        
        st.markdown("---")
        st.subheader("Detailed Growth Analysis")
        candidate_suppliers = supplier_agg.nlargest(10, "Tons")["Exporter"].tolist()
        selected_supplier = st.selectbox("Select Supplier for Detailed Growth Analysis:", candidate_suppliers)
        supplier_data = data[data["Exporter"] == selected_supplier].groupby("Period")["Tons"].sum()
        growth_pct = supplier_data.pct_change() * 100
        growth_df = pd.DataFrame({"Period": growth_pct.index, "Percentage Change (%)": growth_pct.values}).reset_index(drop=True)
        st.markdown(f"#### Period-over-Period Growth for {selected_supplier}")
        st.dataframe(growth_df)

    # ---------------------------
    # Tab 4: Importer Connections
    # ---------------------------
    with tab_importers:
        st.subheader("Importer Connections per Supplier")
        st.markdown("This view shows, for each supplier (Exporter), the relationship with its unique importers (Consignees).")
        
        # Prepare data for the treemap.
        # We want to show a hierarchical view: Outer level is the Supplier and inner level is each unique Importer.
        # To provide meaningful area sizes, we use the sum of Tons per unique connection.
        contrib = data.groupby(["Exporter", "Consignee"])["Tons"].sum().reset_index()
        fig_tree = px.treemap(
            contrib,
            path=["Exporter", "Consignee"],
            values="Tons",
            title="Importer Connections Treemap",
            color="Tons",
            color_continuous_scale="Blues",
            hover_data={"Tons": True}
        )
        st.plotly_chart(fig_tree, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Detailed Importer Connections Table")
        # Create a pivot table that shows, for each supplier, the count of unique importers.
        # First, drop duplicate connections to count each unique relationship only once.
        unique_conn = data.drop_duplicates(subset=["Exporter", "Consignee"])
        pivot_table = unique_conn.groupby("Exporter")["Consignee"].nunique().reset_index()
        pivot_table.columns = ["Exporter", "Unique Importers"]
        pivot_table = pivot_table.sort_values("Unique Importers", ascending=False)
        st.dataframe(pivot_table)

    st.success("✅ Supplier Performance Dashboard Loaded Successfully!")
