import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

def overall_dashboard_report(data: pd.DataFrame):
    st.title("📊 Overall Dashboard Summary Report")
    
    # --- Data Validation ---
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    # Ensure the "Tons" column is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create an ordered "Period" field if not already present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    try:
        data["Period_dt"] = data.apply(lambda row: datetime.strptime(f"{row['Month']} {row['Year']}", "%b %Y"), axis=1)
    except Exception as e:
        st.error("Error parsing Month and Year. Ensure Month is in abbreviated format (e.g., Jan) and Year is numeric.")
        return

    # --- Global Key Metrics ---
    total_imports = data["Tons"].sum()
    total_records = data.shape[0]
    avg_tons = total_imports / total_records if total_records > 0 else 0

    # Top importing state (if available)
    if "Consignee State" in data.columns:
        state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index()
        top_state_row = state_agg.sort_values("Tons", ascending=False).iloc[0]
        top_state_text = f"{top_state_row['Consignee State']} ({top_state_row['Tons']:,.2f} Tons)"
    else:
        top_state_text = "N/A"

    # --- Market Forecast (Linear Regression) ---
    market = data.groupby("Period")["Tons"].sum().reset_index().sort_values("Period")
    if len(market) >= 3:
        market = market.reset_index(drop=True)
        market["TimeIndex"] = market.index
        model = LinearRegression()
        X = market[["TimeIndex"]]
        y = market["Tons"]
        model.fit(X, y)
        next_index = market["TimeIndex"].max() + 1
        forecast_value = model.predict([[next_index]])[0]
        forecast_text = f"Forecast for next period: {forecast_value:,.2f} Tons"
        market["Forecast"] = model.predict(X)
        forecast_row = pd.DataFrame({
            "Period": ["Next Period"],
            "Tons": [np.nan],
            "Forecast": [forecast_value],
            "TimeIndex": [next_index]
        })
        market_forecast = pd.concat([market, forecast_row], ignore_index=True)
    else:
        forecast_text = "Not enough data for forecasting."
        market_forecast = market.copy()

    # --- Layout: Use st.tabs to separate sections ---
    tab_kpis, tab_market, tab_competitor, tab_supplier, tab_state, tab_product, tab_forecast = st.tabs([
        "Key Metrics", "Market Overview", "Competitor Insights", "Supplier Performance", "State Insights", "Product Insights", "Forecasting"
    ])

    # ----- Tab: Key Metrics -----
    with tab_kpis:
        st.subheader("Overall Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Imports (Tons)", f"{total_imports:,.2f}")
        col2.metric("Total Records", total_records)
        col3.metric("Avg Tons per Record", f"{avg_tons:,.2f}")
        col4.metric("Top Importing State", top_state_text)
    
    # ----- Tab: Market Overview -----
    with tab_market:
        st.subheader("Market Overview")
        # Market share by state (if available)
        if "Consignee State" in data.columns:
            state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index()
            fig_state = px.pie(state_agg, names="Consignee State", values="Tons", title="Market Share by State", hole=0.4)
            st.plotly_chart(fig_state, use_container_width=True)
        market_trend = data.groupby("Period")["Tons"].sum().reset_index()
        fig_market = px.line(market_trend, x="Period", y="Tons", title="Overall Market Volume Trend", markers=True)
        st.plotly_chart(fig_market, use_container_width=True)
    
    # ----- Tab: Competitor Insights -----
    with tab_competitor:
        st.subheader("Competitor Insights")
        # Assuming "Consignee" represents competitors.
        comp_summary = data.groupby("Consignee")["Tons"].sum().reset_index()
        top_comp = comp_summary.sort_values("Tons", ascending=False).head(5)
        fig_comp = px.bar(top_comp, x="Consignee", y="Tons", title="Top 5 Competitors by Volume", text_auto=True, color="Tons")
        st.plotly_chart(fig_comp, use_container_width=True)
    
    # ----- Tab: Supplier Performance -----
    with tab_supplier:
        st.subheader("Supplier Performance")
        supplier_agg = data.groupby("Exporter")["Tons"].sum().reset_index()
        top_suppliers = supplier_agg.sort_values("Tons", ascending=False).head(5)
        fig_supplier = px.bar(top_suppliers, x="Exporter", y="Tons", title="Top 5 Suppliers by Volume", text_auto=True, color="Tons")
        st.plotly_chart(fig_supplier, use_container_width=True)
    
    # ----- Tab: State Insights -----
    with tab_state:
        st.subheader("State-Level Insights")
        if "Consignee State" in data.columns:
            state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index()
            fig_state2 = px.bar(state_agg, x="Consignee State", y="Tons", title="Total Imports by State", text_auto=True, color="Tons")
            st.plotly_chart(fig_state2, use_container_width=True)
        else:
            st.info("No state data available.")
    
    # ----- Tab: Product Insights -----
    with tab_product:
        st.subheader("Product Insights")
        if "Product" in data.columns:
            prod_agg = data.groupby("Product")["Tons"].sum().reset_index()
            fig_prod = px.pie(prod_agg, names="Product", values="Tons", title="Market Share by Product Category", hole=0.4)
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.info("Product classification not available.")
    
    # ----- Tab: Forecasting -----
    with tab_forecast:
        st.subheader("Market Forecast")
        if len(market) < 3:
            st.info("Not enough data to generate a forecast.")
        else:
            st.markdown("#### Historical Market Data")
            st.dataframe(market.drop(columns=["TimeIndex"]))
            st.markdown(f"**{forecast_text}**")
            fig_forecast = px.line(market_forecast, x="Period", y="Tons", title="Market Volume Trend and Forecast", markers=True)
            fig_forecast.add_scatter(
                x=market_forecast["Period"],
                y=market_forecast["Forecast"],
                mode="lines+markers",
                name="Forecast",
                line=dict(dash="dash", color="red")
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.success("✅ Overall Dashboard Summary Report Loaded Successfully!")

# To run this module, call overall_dashboard_report(filtered_data) in your main Streamlit app.
