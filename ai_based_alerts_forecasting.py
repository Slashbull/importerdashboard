import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats

def ai_based_alerts_forecasting(data: pd.DataFrame):
    st.title("🔮 AI-Based Alerts & Forecasting Dashboard")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)

    tab_alerts, tab_forecasting = st.tabs(["Alerts", "Forecasting"])
    
    with tab_alerts:
        st.subheader("Competitor Alerts")
        comp_period = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        pct_change = comp_period.pct_change(axis=1) * 100
        pct_change = pct_change.round(2)
        threshold = st.slider("Alert Threshold (% Change)", 0, 100, 20, step=5)
        if pct_change.shape[1] < 2:
            st.info("Not enough periods to compute alerts.")
        else:
            latest_period = pct_change.columns[-1]
            basic_alerts = pct_change[pct_change[latest_period].abs() >= threshold][[latest_period]]
            basic_alerts = basic_alerts.reset_index()
            basic_alerts.columns = ["Competitor", "Latest % Change"]
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
                fig_basic = px.bar(basic_alerts, x="Competitor", y="Latest % Change",
                                   title="Competitors Exceeding Basic Threshold",
                                   labels={"Latest % Change": "% Change"},
                                   text_auto=True, color="Latest % Change",
                                   color_continuous_scale="RdYlGn")
                st.plotly_chart(fig_basic, use_container_width=True)
            st.markdown("### Smart Anomaly Alerts (|Z| > 2)")
            if anomaly_alerts.empty:
                st.success("✅ No anomalies detected based on Z-score.")
            else:
                st.dataframe(anomaly_alerts)
                fig_anomaly = px.bar(anomaly_alerts, x="Competitor", y="Latest % Change (Anomaly)",
                                     title="Competitor Anomaly Alerts",
                                     labels={"Latest % Change (Anomaly)": "% Change"},
                                     text_auto=True, color="Latest % Change (Anomaly)",
                                     color_continuous_scale="RdYlGn")
                st.plotly_chart(fig_anomaly, use_container_width=True)
    
    with tab_forecasting:
        st.subheader("Overall Market Forecast")
        market = data.groupby("Period")["Tons"].sum().reset_index()
        market = market.sort_values("Period")
        st.markdown("#### Historical Market Data")
        st.dataframe(market)
        if len(market) < 3:
            st.info("Not enough data to generate a forecast.")
        else:
            market["Forecast"] = market["Tons"].rolling(window=3).mean()
            forecast_value = market["Forecast"].iloc[-1]
            forecast_df = pd.DataFrame({"Period": ["Next Period"], "Tons": [np.nan], "Forecast": [forecast_value]})
            market_forecast = pd.concat([market, forecast_df], ignore_index=True)
            st.markdown("#### Market Forecast Data")
            st.dataframe(market_forecast)
            fig_forecast = px.line(market_forecast, x="Period", y="Tons",
                                   title="Market Volume Trend and Forecast", markers=True)
            fig_forecast.add_scatter(x=market_forecast["Period"], y=market_forecast["Forecast"],
                                     mode="lines+markers", name="Forecast",
                                     line=dict(dash="dash", color="red"))
            st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.success("✅ AI-Based Alerts & Forecasting Dashboard Loaded Successfully!")
