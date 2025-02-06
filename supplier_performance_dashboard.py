import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def supplier_performance_dashboard(data: pd.DataFrame):
    st.title("📊 Supplier Performance Dashboard")
    
    # Verify required columns (we need Exporter, Consignee, Tons, Month, Year)
    required_columns = ["Exporter", "Consignee", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure the Tons column is numeric and create a Period column for time-based analysis
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    data["Period"] = data["Month"] + "-" + data["Year"].astype(str)

    # Create a tabbed layout for the dashboard sections
    tab_metrics, tab_top, tab_trends, tab_risk, tab_importers = st.tabs([
        "Key Metrics", "Top Suppliers", "Trends", "Risk Analysis", "Importer Connections"
    ])

    # ---------------------------
    # Tab 1: Key Metrics
    # ---------------------------
    with tab_metrics:
        st.subheader("Supplier Performance Key Metrics")
        total_tons = data["Tons"].sum()
        unique_suppliers = data["Exporter"].nunique()
        avg_tons_supplier = total_tons / unique_suppliers if unique_suppliers > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tons", f"{total_tons:,.2f}")
        col2.metric("Unique Suppliers", unique_suppliers)
        col3.metric("Avg Tons per Supplier", f"{avg_tons_supplier:,.2f}")

    # ---------------------------
    # Tab 2: Top Suppliers
    # ---------------------------
    with tab_top:
        st.subheader("Top Suppliers by Volume")
        top_n = st.selectbox("Select number of top suppliers to display:", options=[5, 10, 15], index=0)
        top_suppliers = (
            data.groupby("Exporter")["Tons"]
            .sum()
            .nlargest(top_n)
            .reset_index()
        )
        fig_top = px.bar(
            top_suppliers,
            x="Exporter",
            y="Tons",
            title=f"Top {top_n} Suppliers by Tons",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig_top, use_container_width=True)

    # ---------------------------
    # Tab 3: Trends
    # ---------------------------
    with tab_trends:
        st.subheader("Supplier Trends Over Time")
        trends_df = data.groupby(["Exporter", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(trends_df)

    # ---------------------------
    # Tab 4: Risk Analysis
    # ---------------------------
    with tab_risk:
        st.subheader("Risk Analysis")
        st.info("Adjust the risk threshold (percentage of the mean) to flag suppliers with high variability in performance.")
        threshold = st.slider("Risk Threshold (% Variation)", 0, 100, 50, step=5)
        # Calculate aggregate statistics per supplier
        stats = data.groupby("Exporter")["Tons"].agg(["sum", "mean", "std"])
        # Flag suppliers where standard deviation exceeds threshold percentage of the mean
        risky_suppliers = stats[stats["std"] > (stats["mean"] * (threshold / 100))]
        st.markdown("#### Suppliers with High Variability")
        st.dataframe(risky_suppliers)
        if not risky_suppliers.empty:
            fig_risk = px.bar(
                risky_suppliers.reset_index(),
                x="Exporter",
                y="std",
                title="Risky Suppliers by Standard Deviation",
                labels={"std": "Standard Deviation (Tons)"},
                text_auto=True
            )
            st.plotly_chart(fig_risk, use_container_width=True)

    # ---------------------------
    # Tab 5: Importer Connections
    # ---------------------------
    with tab_importers:
        st.subheader("Importer Connections per Supplier")
        # For each supplier (Exporter), count the number of unique importers (Consignee)
        connection_df = data.groupby("Exporter")["Consignee"].nunique().reset_index()
        connection_df.columns = ["Exporter", "Unique Importers"]
        # Sort by the number of importers
        connection_df = connection_df.sort_values(by="Unique Importers", ascending=False)
        st.dataframe(connection_df)
        fig_connections = px.bar(
            connection_df,
            x="Exporter",
            y="Unique Importers",
            title="Number of Importers Connected with Each Supplier",
            labels={"Unique Importers": "Unique Importers Count"},
            text_auto=True
        )
        st.plotly_chart(fig_connections, use_container_width=True)

    st.success("✅ Supplier Performance Dashboard Loaded Successfully!")
