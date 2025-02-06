import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def supplier_performance_dashboard(data: pd.DataFrame):
    st.title("📊 Supplier Performance Dashboard")
    
    # -------------------------------------------------------------------------
    # Data & Column Validation
    # -------------------------------------------------------------------------
    required_columns = ["Exporter", "Consignee", "Tons", "Month", "Year"]
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure "Tons" is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a "Period" column if not present (format: Month-Year).
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Define a month ordering dictionary for potential time-series sorting.
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    # -------------------------------------------------------------------------
    # Tabbed Layout: Key Metrics, Top Suppliers, Trends & Risk Analysis, Detailed Analysis
    # -------------------------------------------------------------------------
    tab_kpis, tab_top, tab_trends, tab_detail = st.tabs([
        "Key Metrics", "Top Suppliers", "Trends & Risk Analysis", "Detailed Analysis"
    ])

    # ---------------------------
    # Tab 1: Key Metrics
    # ---------------------------
    with tab_kpis:
        st.subheader("Supplier Key Performance Indicators")
        # Aggregate supplier volumes.
        supplier_agg = data.groupby("Exporter")["Tons"].sum().reset_index()
        total_volume = supplier_agg["Tons"].sum()
        num_suppliers = supplier_agg["Exporter"].nunique()
        avg_volume = total_volume / num_suppliers if num_suppliers > 0 else 0

        # Compute risk metrics for each supplier (based on overall volumes).
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
        st.subheader("Overall Supplier Trends")
        # Pivot table: rows = Exporter, columns = Period, values = Tons.
        trends_df = data.groupby(["Exporter", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(trends_df)
        
        st.markdown("---")
        st.subheader("Detailed Growth Analysis")
        candidate_suppliers = supplier_agg.nlargest(10, "Tons")["Exporter"].tolist()
        selected_supplier = st.selectbox("Select Supplier for Growth Analysis:", candidate_suppliers)
        supplier_data = data[data["Exporter"] == selected_supplier].groupby("Period")["Tons"].sum()
        growth_pct = supplier_data.pct_change() * 100
        growth_df = pd.DataFrame({
            "Period": growth_pct.index,
            "Percentage Change (%)": growth_pct.values
        }).reset_index(drop=True)
        st.markdown(f"#### Period-over-Period Growth for {selected_supplier}")
        st.dataframe(growth_df)

    # ---------------------------
    # Tab 4: Detailed Analysis (Drill‑Down, Forecasting & Anomaly Detection)
    # ---------------------------
    with tab_detail:
        st.subheader("Detailed Supplier Analysis")
        st.markdown("Select a supplier to view a detailed monthly breakdown, a forecast for the next period, and anomaly detection based on historical performance.")
        # For detailed analysis, let the user select from top 10 suppliers.
        candidate_suppliers_detail = supplier_agg.nlargest(10, "Tons")["Exporter"].tolist()
        selected_detail = st.selectbox("Select a Supplier for Detailed Analysis:", candidate_suppliers_detail)
        detail_data = data[data["Exporter"] == selected_detail].groupby("Period")["Tons"].sum().reset_index()
        
        # Ensure the data is sorted chronologically based on a custom order if possible.
        # Here, we assume the period strings sort in a roughly chronological order.
        detail_data = detail_data.sort_values("Period")
        
        st.markdown("#### Monthly Volume Data")
        st.dataframe(detail_data)

        # Forecasting: Use a simple rolling average to forecast the next period.
        window = st.slider("Select Forecast Window (number of periods):", 2, 6, 3, step=1)
        if len(detail_data) >= window:
            forecast_value = detail_data["Tons"].rolling(window=window).mean().iloc[-1]
        else:
            forecast_value = np.nan
        
        st.markdown("#### Forecast for Next Period")
        st.write(f"Forecasted Volume for Next Period: **{forecast_value:,.2f} Tons**")
        
        # Anomaly Detection: Compute z-scores for the supplier’s monthly volumes.
        volumes = detail_data["Tons"]
        mean_vol = volumes.mean()
        std_vol = volumes.std()
        # Avoid division by zero
        if std_vol > 0:
            z_scores = (volumes - mean_vol) / std_vol
        else:
            z_scores = volumes - mean_vol  # all zeros if std is zero
        # Flag anomalies: here we use a threshold of 2 (i.e., values beyond ±2 standard deviations).
        anomaly_threshold = st.number_input("Anomaly Threshold (z-score):", value=2.0, step=0.1)
        detail_data["Z-Score"] = z_scores
        detail_data["Anomaly"] = detail_data["Z-Score"].apply(lambda x: "Yes" if abs(x) >= anomaly_threshold else "No")
        
        st.markdown("#### Detailed Analysis with Anomaly Detection")
        st.dataframe(detail_data)
        
        # Plot the historical volumes with anomaly markers and forecast value.
        fig_detail = px.line(detail_data, x="Period", y="Tons", title=f"Monthly Volume Trend for {selected_detail}", markers=True)
        # Mark anomalies with red markers.
        anomalies = detail_data[detail_data["Anomaly"] == "Yes"]
        if not anomalies.empty:
            fig_detail.add_scatter(x=anomalies["Period"], y=anomalies["Tons"],
                                   mode="markers", marker=dict(color="red", size=10),
                                   name="Anomaly")
        # Append forecast as the next period (using a dummy label)
        if not np.isnan(forecast_value):
            last_period = detail_data["Period"].iloc[-1]
            # Create a dummy next period label (this can be refined further)
            next_period = f"{last_period}*"
            fig_detail.add_scatter(x=[next_period], y=[forecast_value],
                                   mode="markers", marker=dict(color="green", size=12),
                                   name="Forecast")
        st.plotly_chart(fig_detail, use_container_width=True)

    st.success("✅ Supplier Performance Dashboard Loaded Successfully!")
