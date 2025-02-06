import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def ensure_period_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure that a 'Period' column exists by concatenating Month and Year.
    """
    if "Period" not in df.columns:
        df["Period"] = df["Month"] + "-" + df["Year"].astype(str)
    return df

def compute_competitor_pct_change(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each competitor (Consignee), compute the period-over-period percentage change in Tons.
    Returns a DataFrame with the latest percentage change for each competitor.
    """
    # Ensure the Period column exists
    df = ensure_period_column(df)
    # Group data by competitor and period
    comp_period = df.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
    # Calculate the percentage change along the periods (axis=1)
    pct_change = comp_period.pct_change(axis=1) * 100
    # Get the latest available percentage change for each competitor
    latest_pct_change = pct_change.iloc[:, -1].reset_index()
    latest_pct_change.columns = ["Consignee", "Latest % Change"]
    return latest_pct_change

def forecast_market(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """
    Compute a basic forecast for the overall market based on a rolling window average.
    Aggregates total Tons by period, then forecasts the next period as the average
    of the last 'window' periods.
    Returns a DataFrame with historical data and one forecast row appended.
    """
    # Ensure the Period column exists
    df = ensure_period_column(df)
    market = df.groupby("Period")["Tons"].sum().reset_index()
    # Sort the periods (we assume that the Period strings sort chronologically;
    # if not, additional ordering logic may be required)
    market = market.sort_values("Period")
    
    # Compute rolling mean forecast; forecast next period as average of last `window` periods
    if len(market) >= window:
        forecast_value = market["Tons"].rolling(window=window).mean().iloc[-1]
    else:
        forecast_value = np.nan  # Not enough data to forecast
    
    # Append the forecast as a new row; we label the period as "Next Period"
    forecast_df = pd.DataFrame({
        "Period": ["Next Period"],
        "Tons": [forecast_value]
    })
    market_forecast = pd.concat([market, forecast_df], ignore_index=True)
    return market_forecast

def ai_based_alerts_forecasting(data: pd.DataFrame):
    st.title("🔮 AI-Based Alerts & Forecasting Dashboard")
    
    # Check that data exists and required columns are present
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return
    required_columns = ["Consignee", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure the Tons column is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    data = ensure_period_column(data)

    # Create a tabbed layout: one tab for Alerts, one for Forecasting
    tab_alerts, tab_forecast = st.tabs(["Alerts", "Forecasting"])

    # ============================
    # Tab 1: Alerts
    # ============================
    with tab_alerts:
        st.subheader("Competitor Alerts")
        st.info("Adjust the threshold below to flag competitors with high growth or decline.")
        # Let user set the threshold (default 20% for growth and -20% for decline)
        threshold = st.slider("Alert Threshold (% Change)", 0, 100, 20, step=5)
        
        # Compute the latest percentage change for each competitor
        pct_change_df = compute_competitor_pct_change(data)
        
        # Filter alerts: show competitors with a positive change above threshold OR negative change below -threshold
        alerts_df = pct_change_df[(pct_change_df["Latest % Change"] >= threshold) |
                                  (pct_change_df["Latest % Change"] <= -threshold)]
        
        if alerts_df.empty:
            st.success("✅ No competitors exceed the threshold for alerts.")
        else:
            st.markdown("### Competitors Exceeding the Threshold")
            st.dataframe(alerts_df)
            # Optionally, display a bar chart of the alerts
            fig_alerts = px.bar(alerts_df, x="Consignee", y="Latest % Change",
                                title="Competitor Percentage Change Alerts",
                                labels={"Latest % Change": "% Change"},
                                text_auto=True)
            st.plotly_chart(fig_alerts, use_container_width=True)

    # ============================
    # Tab 2: Forecasting
    # ============================
    with tab_forecast:
        st.subheader("Overall Market Forecast")
        # Compute the forecast for the overall market using a rolling window average
        forecast_df = forecast_market(data, window=3)
        
        # Display the historical data and forecast in a table
        st.markdown("#### Historical Market Data with Forecast")
        st.dataframe(forecast_df)
        
        # Create a line chart showing historical market Tons and the forecast as the final point
        fig_forecast = px.line(
            forecast_df,
            x="Period",
            y="Tons",
            title="Market Tons Trend with Forecast",
            markers=True
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.success("✅ AI-Based Alerts & Forecasting Dashboard Loaded Successfully!")
