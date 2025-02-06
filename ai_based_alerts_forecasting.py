import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats  # For Z-score computation

def ai_based_alerts_forecasting(data: pd.DataFrame):
    st.title("🔮 AI-Based Alerts & Forecasting Dashboard")
    
    # -----------------------------
    # Data Validation & Preprocessing
    # -----------------------------
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert Tons to numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Create a 'Period' column (format: Month-Year) if not present
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)

    # -----------------------------
    # Tabbed Layout: Alerts and Forecasting
    # -----------------------------
    tab_alerts, tab_forecasting = st.tabs(["Alerts", "Forecasting"])

    # -----------------------------
    # Alerts Tab: Smart Anomaly Detection and Threshold Alerts
    # -----------------------------
    with tab_alerts:
        st.subheader("Competitor Alerts")
        
        # Group by competitor (Consignee) and period; sum Tons per period
        comp_period = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        
        # Compute period-over-period percentage change
        pct_change = comp_period.pct_change(axis=1) * 100
        pct_change = pct_change.round(2)
        
        # Prepare a default alert threshold slider (e.g., 20% by default)
        threshold = st.slider("Alert Threshold (% Change)", min_value=0, max_value=100, value=20, step=5)
        
        # Determine the most recent period if available
        if pct_change.shape[1] < 2:
            st.info("Not enough periods to compute alerts.")
        else:
            latest_period = pct_change.columns[-1]
            # Basic threshold alerts: competitors whose absolute change exceeds the threshold
            basic_alerts = pct_change[pct_change[latest_period].abs() >= threshold][[latest_period]]
            basic_alerts = basic_alerts.reset_index()
            basic_alerts.columns = ["Competitor", "Latest % Change"]

            # Smart anomaly detection using Z-score: flag changes with |Z| > 2
            all_changes = pct_change[latest_period].dropna()
            if not all_changes.empty:
                z_scores = np.abs(stats.zscore(all_changes))
                anomaly_alerts = all_changes[z_scores > 2].reset_index()
                anomaly_alerts.columns = ["Competitor", "Latest % Change (Anomaly)"]
            else:
                anomaly_alerts = pd.DataFrame()

            st.markdown("### Basic Threshold Alerts")
            if basic_alerts.empty:
                st.success("✅ No competitors exceed the basic threshold.")
            else:
                st.dataframe(basic_alerts)
                fig_basic = px.bar(
                    basic_alerts,
                    x="Competitor",
                    y="Latest % Change",
                    title="Competitors Exceeding Basic Threshold",
                    labels={"Latest % Change": "% Change"},
                    text_auto=True,
                    color="Latest % Change",
                    color_continuous_scale="RdYlGn"
                )
                st.plotly_chart(fig_basic, use_container_width=True)

            st.markdown("### Smart Anomaly Alerts (|Z| > 2)")
            if anomaly_alerts.empty:
                st.success("✅ No anomalies detected based on Z-score.")
            else:
                st.dataframe(anomaly_alerts)
                fig_anomaly = px.bar(
                    anomaly_alerts,
                    x="Competitor",
                    y="Latest % Change (Anomaly)",
                    title="Competitor Anomaly Alerts",
                    labels={"Latest % Change (Anomaly)": "% Change"},
                    text_auto=True,
                    color="Latest % Change (Anomaly)",
                    color_continuous_scale="RdYlGn"
                )
                st.plotly_chart(fig_anomaly, use_container_width=True)

    # -----------------------------
    # Forecasting Tab: Rolling Average Forecast
    # -----------------------------
    with tab_forecasting:
        st.subheader("Overall Market Forecast")
        # Aggregate overall market volume by Period
        market = data.groupby("Period")["Tons"].sum().reset_index()
        
        # Sort periods chronologically
        # For simplicity, we assume "Period" sorts correctly (if needed, additional parsing can be added)
        market = market.sort_values("Period")
        
        st.markdown("#### Historical Market Data")
        st.dataframe(market)
        
        if len(market) < 3:
            st.info("Not enough data to generate a forecast.")
        else:
            # Calculate rolling average as forecast (window = 3)
            market["Forecast"] = market["Tons"].rolling(window=3).mean()
            forecast_value = market["Tons"].rolling(window=3).mean().iloc[-1]
            # Append forecast as a new row
            forecast_df = pd.DataFrame({
                "Period": ["Next Period"],
                "Tons": [np.nan],
                "Forecast": [forecast_value]
            })
            market_forecast = pd.concat([market, forecast_df], ignore_index=True)
            
            st.markdown("#### Market Forecast Data")
            st.dataframe(market_forecast)
            
            # Plot historical data and forecast as a combined line chart
            fig_forecast = px.line(
                market_forecast,
                x="Period",
                y="Tons",
                title="Market Volume Trend and Forecast",
                markers=True
            )
            # Overlay forecast line
            fig_forecast.add_scatter(
                x=market_forecast["Period"],
                y=market_forecast["Forecast"],
                mode="lines+markers",
                name="Forecast",
                line=dict(dash="dash", color="red")
            )
            st.plotly_chart(fig_forecast, use_container_width=True)

    st.success("✅ AI-Based Alerts & Forecasting Dashboard Loaded Successfully!")
