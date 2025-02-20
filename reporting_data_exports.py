import streamlit as st
import pandas as pd
import io
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.express as px

# =============================================================================
# SUMMARY & INSIGHTS FUNCTIONS
# =============================================================================
def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary DataFrame with key metrics.
    Metrics include:
      - Total Imports (Tons)
      - Total Records
      - Average Tons per Record
    """
    total_tons = df["Tons"].sum()
    total_records = df.shape[0]
    avg_tons = total_tons / total_records if total_records > 0 else 0

    summary_data = {
        "Metric": ["Total Imports (Tons)", "Total Records", "Average Tons per Record"],
        "Value": [f"{total_tons:,.2f}", total_records, f"{avg_tons:,.2f}"]
    }
    return pd.DataFrame(summary_data)

def generate_auto_insights(df: pd.DataFrame) -> str:
    """
    Generate a natural‑language summary of key insights from the data.
    For example: total imports, top importing state, and peak year.
    """
    try:
        total_tons = df["Tons"].sum()
        total_records = df.shape[0]
        avg_tons = total_tons / total_records if total_records > 0 else 0
        insights = []
        insights.append(f"Total imports are {total_tons:,.2f} tons over {total_records} records, averaging {avg_tons:,.2f} tons per record.")
        if "Consignee State" in df.columns:
            state_agg = df.groupby("Consignee State")["Tons"].sum()
            top_state = state_agg.idxmax()
            top_state_tons = state_agg.max()
            insights.append(f"The top importing state is {top_state} with {top_state_tons:,.2f} tons.")
        if "Year" in df.columns:
            year_agg = df.groupby("Year")["Tons"].sum()
            top_year = year_agg.idxmax()
            top_year_tons = year_agg.max()
            insights.append(f"Peak year: {top_year} with {top_year_tons:,.2f} tons.")
        return " ".join(insights)
    except Exception:
        return "Insights not available."

# =============================================================================
# EXPORT FUNCTIONS (CSV and Excel only)
# =============================================================================
def export_to_csv(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Export selected columns to CSV.
    If summary or insights are enabled, prepend them as commented lines.
    """
    data_to_export = df[columns]
    csv_buffer = io.StringIO()
    if include_summary or include_insights:
        csv_buffer.write("# Auto‑Generated Report Summary\n")
        if include_summary:
            summary_df = generate_summary(df)
            for _, row in summary_df.iterrows():
                csv_buffer.write(f"# {row['Metric']}: {row['Value']}\n")
        if include_insights:
            csv_buffer.write(f"# Insights: {generate_auto_insights(df)}\n")
        csv_buffer.write("\n")
    data_to_export.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")

def export_to_excel(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Export selected columns to an Excel file with two sheets:
      - "Data": Main report data.
      - "Summary": Key metrics and auto‑generated insights.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[columns].to_excel(writer, index=False, sheet_name="Data")
        if include_summary or include_insights:
            summary_df = generate_summary(df)
            insights_text = generate_auto_insights(df) if include_insights else ""
            insights_df = pd.DataFrame({"Auto Insights": [insights_text]})
            summary_combined = pd.concat([summary_df, insights_df], ignore_index=True)
            summary_combined.to_excel(writer, index=False, sheet_name="Summary")
    return output.getvalue()

# =============================================================================
# OVERALL DASHBOARD REPORT (INTERACTIVE)
# =============================================================================
def overall_dashboard_report(data: pd.DataFrame):
    st.title("📊 Overall Dashboard Summary Report")
    
    # --- Data Validation & Preprocessing ---
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return
    
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Global KPIs
    total_imports = data["Tons"].sum()
    total_records = data.shape[0]
    avg_tons = total_imports / total_records if total_records > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Imports (Tons)", f"{total_imports:,.2f}")
    col2.metric("Total Records", total_records)
    col3.metric("Avg Tons per Record", f"{avg_tons:,.2f}")
    if "Consignee State" in data.columns:
        state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index()
        top_state = state_agg.sort_values("Tons", ascending=False).iloc[0]
        col4.metric("Top State", f"{top_state['Consignee State']} ({top_state['Tons']:,.2f} Tons)")
    else:
        col4.metric("Top State", "N/A")
    
    st.markdown("---")
    st.subheader("Interactive Charts")
    
    # Create tabs for different aspects of the dashboard report.
    tabs = st.tabs([
        "Market Overview", 
        "Competitor Insights", 
        "Supplier Performance", 
        "State Insights", 
        "Product Insights", 
        "Forecasting"
    ])
    
    # Market Overview Tab
    with tabs[0]:
        st.markdown("#### Overall Market Volume Trend")
        market_trend = data.groupby("Period")["Tons"].sum().reset_index()
        fig_market = px.line(market_trend, x="Period", y="Tons", title="Market Volume Trend", markers=True)
        st.plotly_chart(fig_market, use_container_width=True)
    
    # Competitor Insights Tab
    with tabs[1]:
        st.markdown("#### Top Competitors by Volume")
        comp_summary = data.groupby("Consignee")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        fig_comp = px.bar(comp_summary.head(5), x="Consignee", y="Tons", title="Top 5 Competitors", text_auto=True, color="Tons")
        st.plotly_chart(fig_comp, use_container_width=True)
    
    # Supplier Performance Tab
    with tabs[2]:
        st.markdown("#### Top Suppliers by Volume")
        supplier_agg = data.groupby("Exporter")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        fig_supplier = px.bar(supplier_agg.head(5), x="Exporter", y="Tons", title="Top 5 Suppliers", text_auto=True, color="Tons")
        st.plotly_chart(fig_supplier, use_container_width=True)
    
    # State Insights Tab
    with tabs[3]:
        st.markdown("#### Imports by State")
        if "Consignee State" in data.columns:
            state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
            fig_state = px.bar(state_agg, x="Consignee State", y="Tons", title="Imports by State", text_auto=True, color="Tons")
            st.plotly_chart(fig_state, use_container_width=True)
        else:
            st.info("State data not available.")
    
    # Product Insights Tab
    with tabs[4]:
        st.markdown("#### Market Share by Product Category")
        if "Product" in data.columns:
            prod_agg = data.groupby("Product")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
            fig_prod = px.pie(prod_agg, names="Product", values="Tons", title="Product Market Share", hole=0.4)
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.info("Product classification not available.")
    
    # Forecasting Tab
    with tabs[5]:
        st.markdown("#### Market Forecast")
        market_df = data.groupby("Period")["Tons"].sum().reset_index().sort_values("Period").reset_index(drop=True)
        if len(market_df) < 3:
            st.info("Not enough data to generate a forecast.")
        else:
            market_df["TimeIndex"] = market_df.index
            model = LinearRegression()
            X = market_df[["TimeIndex"]]
            y = market_df["Tons"]
            model.fit(X, y)
            next_index = market_df["TimeIndex"].max() + 1
            forecast_value = model.predict([[next_index]])[0]
            forecast_text = f"Forecast for next period: {forecast_value:,.2f} Tons"
            market_df["Forecast"] = model.predict(X)
            forecast_row = pd.DataFrame({
                "Period": ["Next Period"],
                "Tons": [None],
                "Forecast": [forecast_value],
                "TimeIndex": [next_index]
            })
            market_forecast = pd.concat([market_df, forecast_row], ignore_index=True)
            st.markdown(f"**{forecast_text}**")
            fig_forecast = px.line(market_forecast, x="Period", y="Tons", title="Market Forecast", markers=True)
            fig_forecast.add_scatter(
                x=market_forecast["Period"],
                y=market_forecast["Forecast"],
                mode="lines+markers",
                name="Forecast",
                line=dict(dash="dash", color="red")
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Overall Report Summary")
    st.dataframe(generate_summary(data))
    st.markdown(f"**Auto Insights:** {generate_auto_insights(data)}")
    
    st.success("✅ Overall Dashboard Summary Report Loaded Successfully!")

# =============================================================================
# MAIN REPORTING & EXPORT FUNCTION
# =============================================================================
def reporting_data_exports(data: pd.DataFrame):
    st.title("📄 Reporting & Data Exports Dashboard")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    all_columns = list(data.columns)
    selected_columns = st.multiselect("Select Columns to Include in Report:", options=all_columns, default=all_columns)
    include_summary = st.checkbox("Include Summary Metrics", value=True)
    include_insights = st.checkbox("Include Auto Insights", value=True)
    
    st.markdown("### Report Preview")
    preview_df = data[selected_columns].copy()
    st.dataframe(preview_df.head(50))
    
    st.markdown("### Export Options")
    report_format = st.radio("Report Format:", ("CSV", "Excel"))
    
    if report_format == "CSV":
        csv_data = export_to_csv(data, selected_columns, include_summary, include_insights)
        st.download_button("📥 Download CSV Report", csv_data, "report.csv", "text/csv")
    elif report_format == "Excel":
        excel_data = export_to_excel(data, selected_columns, include_summary, include_insights)
        st.download_button("📥 Download Excel Report", excel_data, "report.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.success("✅ Report Generation Ready!")
