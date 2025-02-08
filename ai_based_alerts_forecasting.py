import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

def advanced_anomaly_alerts(pct_series: pd.Series, contamination: float = 0.1) -> pd.DataFrame:
    """
    Use an IsolationForest to detect anomalies in a percentage change series.
    
    Parameters:
        pct_series (pd.Series): A pandas Series of percentage changes.
        contamination (float): The proportion of outliers expected in the data (default 0.1).
        
    Returns:
        pd.DataFrame: A DataFrame with anomalies (rows where the model flags as -1).
    """
    # Reshape data to a 2D array.
    X = pct_series.values.reshape(-1, 1)
    # Fit an IsolationForest.
    clf = IsolationForest(contamination=contamination, random_state=42)
    preds = clf.fit_predict(X)
    anomalies = pct_series[preds == -1]
    return anomalies.reset_index().rename(columns={"index": "Competitor", 0: "Anomaly Score"})

def forecast_market_volume(market_df: pd.DataFrame) -> (pd.DataFrame, float):
    """
    Fit a simple linear regression model to forecast the next period's market volume.
    This function assumes that market_df has a "Period" column (sorted) and a "Tons" column.
    
    Returns:
        market_forecast (pd.DataFrame): A DataFrame containing historical data with an additional
          row for the forecasted next period.
        forecast_value (float): The predicted market volume for the next period.
    """
    # Create a time index based on the order of periods.
    market_df = market_df.sort_values("Period").reset_index(drop=True)
    market_df["TimeIndex"] = market_df.index
    # Prepare features and target.
    X = market_df[["TimeIndex"]]
    y = market_df["Tons"]
    
    # Fit a Linear Regression model.
    model = LinearRegression()
    model.fit(X, y)
    # Forecast next period: next time index.
    next_index = np.array([[market_df["TimeIndex"].max() + 1]])
    forecast_value = model.predict(next_index)[0]
    # Append the forecast row.
    forecast_row = pd.DataFrame({
        "Period": ["Next Period"],
        "Tons": [np.nan],
        "Forecast": [forecast_value],
        "TimeIndex": [market_df["TimeIndex"].max() + 1]
    })
    # Create a forecast DataFrame with historical Tons and forecast.
    market_df["Forecast"] = model.predict(X)
    market_forecast = pd.concat([market_df, forecast_row], ignore_index=True)
    return market_forecast, forecast_value

def ai_based_alerts_forecasting(data: pd.DataFrame):
    st.title("🔮 AI-Based Alerts & Forecasting Dashboard")
    
    # --- Data Validation ---
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert Tons to numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a "Period" field if not already present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # --- Tab Layout: Alerts and Forecasting ---
    tab_alerts, tab_forecasting = st.tabs(["Alerts", "Forecasting"])
    
    # ----- Tab 1: Alerts -----
    with tab_alerts:
        st.subheader("Competitor Alerts")
        # Aggregate competitor volumes by Period.
        comp_period = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        
        # Calculate period-over-period percentage change.
        pct_change = comp_period.pct_change(axis=1) * 100
        pct_change = pct_change.round(2)
        
        # Basic threshold alerts.
        threshold = st.slider("Alert Threshold (% Change)", min_value=0, max_value=100, value=20, step=5, key="alert_threshold")
        
        if pct_change.shape[1] < 2:
            st.info("Not enough periods to compute alerts.")
        else:
            latest_period = pct_change.columns[-1]
            basic_alerts = pct_change[pct_change[latest_period].abs() >= threshold][[latest_period]]
            basic_alerts = basic_alerts.reset_index()
            basic_alerts.columns = ["Competitor", "Latest % Change"]
            
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
            
            # Advanced anomaly detection using IsolationForest.
            anomalies = advanced_anomaly_alerts(pct_change[latest_period])
            st.markdown("### Advanced Anomaly Alerts (IsolationForest)")
            if anomalies.empty:
                st.success("✅ No anomalies detected using advanced methods.")
            else:
                anomalies.rename(columns={"Competitor": "Index"}, inplace=True)
                # Map the index back to competitor names.
                anomalies["Competitor"] = pct_change.index[anomalies["Index"]]
                st.dataframe(anomalies[["Competitor", "Latest % Change (Anomaly)"]])
                fig_anomaly = px.bar(
                    anomalies,
                    x="Competitor",
                    y="Latest % Change (Anomaly)",
                    title="Competitor Anomaly Alerts (Advanced)",
                    labels={"Latest % Change (Anomaly)": "% Change"},
                    text_auto=True,
                    color="Latest % Change (Anomaly)",
                    color_continuous_scale="RdYlGn"
                )
                st.plotly_chart(fig_anomaly, use_container_width=True)
    
    # ----- Tab 2: Forecasting -----
    with tab_forecasting:
        st.subheader("Overall Market Forecast")
        # Aggregate overall market volume by Period.
        market = data.groupby("Period")["Tons"].sum().reset_index()
        market = market.sort_values("Period").reset_index(drop=True)
        st.markdown("#### Historical Market Data")
        st.dataframe(market)
        
        if len(market) < 3:
            st.info("Not enough data to generate a forecast.")
        else:
            # Create a time index for forecasting.
            market["TimeIndex"] = market.index
            # Fit a linear regression model to forecast the next period.
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            X = market[["TimeIndex"]]
            y = market["Tons"]
            model.fit(X, y)
            forecast_value = model.predict([[market["TimeIndex"].max() + 1]])[0]
            
            # Build forecast DataFrame.
            market["Forecast"] = model.predict(X)
            forecast_df = pd.DataFrame({
                "Period": ["Next Period"],
                "Tons": [np.nan],
                "Forecast": [forecast_value],
                "TimeIndex": [market["TimeIndex"].max() + 1]
            })
            market_forecast = pd.concat([market, forecast_df], ignore_index=True)
            
            st.markdown("#### Market Forecast Data")
            st.dataframe(market_forecast)
            
            fig_forecast = px.line(
                market_forecast,
                x="Period",
                y="Tons",
                title="Market Volume Trend and Forecast",
                markers=True
            )
            fig_forecast.add_scatter(
                x=market_forecast["Period"],
                y=market_forecast["Forecast"],
                mode="lines+markers",
                name="Forecast",
                line=dict(dash="dash", color="red")
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.success("✅ AI-Based Alerts & Forecasting Dashboard Loaded Successfully!")
