import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def supplier_performance_dashboard(data: pd.DataFrame):
    st.title("📊 Supplier Performance Dashboard")
    
    # Check for required data and columns
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert Tons column to numeric and create a Period column
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    data["Period"] = data["Month"] + "-" + data["Year"].astype(str)

    # Create a tabbed layout for the supplier performance dashboard
    tab_metrics, tab_top, tab_trends, tab_risk, tab_mapping = st.tabs([
        "Key Metrics", "Top Suppliers", "Trends", "Risk Analysis", "Mapping & Contribution"
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
        top_suppliers = data.groupby("Exporter")["Tons"].sum().nlargest(top_n).reset_index()
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
        st.info("Adjust the risk threshold to flag suppliers with high variability in performance.")
        threshold = st.slider("Risk Threshold (% Variation)", 0, 100, 50, step=5)
        # Calculate aggregate statistics per supplier
        stats = data.groupby("Exporter")["Tons"].agg(["sum", "mean", "std"])
        # Flag suppliers where the standard deviation exceeds the specified percentage of the mean
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
    # Tab 5: Mapping & Contribution
    # ---------------------------
    with tab_mapping:
        st.subheader("Supplier Contribution Mapping")
        st.info("This map visualizes supplier contributions using a dummy location mapping. Update with real coordinates as needed.")

        # Dummy mapping dictionary for supplier locations (replace with real data if available)
        dummy_supplier_locations = {
            "Delight Oasis Trading Co": {"lat": 28.6139, "lon": 77.2090},
            "Siafa International Industry Company": {"lat": 19.0760, "lon": 72.8777},
            "Dar Alhijra Dates Factory Company": {"lat": 12.9716, "lon": 77.5946},
            "ABDUL RAHIM MOHAMMAD NOOR TRADING ESTABLISHMENT": {"lat": 26.9124, "lon": 75.7873},
            # Add more mappings as required...
        }
        # Aggregate supplier contributions
        supplier_contrib = data.groupby("Exporter")["Tons"].sum().reset_index()
        # Map each supplier to coordinates if available
        supplier_contrib["lat"] = supplier_contrib["Exporter"].apply(lambda x: dummy_supplier_locations.get(x, {}).get("lat", np.nan))
        supplier_contrib["lon"] = supplier_contrib["Exporter"].apply(lambda x: dummy_supplier_locations.get(x, {}).get("lon", np.nan))
        mapped_suppliers = supplier_contrib.dropna(subset=["lat", "lon"])
        if mapped_suppliers.empty:
            st.info("No location data available for suppliers.")
        else:
            # Plot the map using Plotly Express with open-street-map style (no token required)
            fig_map = px.scatter_mapbox(
                mapped_suppliers,
                lat="lat",
                lon="lon",
                size="Tons",
                hover_name="Exporter",
                hover_data={"Tons": True, "lat": False, "lon": False},
                color="Tons",
                zoom=4,
                height=500,
                title="Supplier Contribution Map"
            )
            fig_map.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig_map, use_container_width=True)

    st.success("✅ Supplier Performance Dashboard Loaded Successfully!")
