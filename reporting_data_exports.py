import streamlit as st
import pandas as pd
import io
from datetime import datetime
from sklearn.linear_model import LinearRegression

def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary DataFrame with key metrics:
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
    Generate a textual summary of key insights from the data.
    For example: total imports, top importing state, and peak year.
    """
    try:
        total_tons = df["Tons"].sum()
        total_records = df.shape[0]
        avg_tons = total_tons / total_records if total_records > 0 else 0
        insights = []
        insights.append(f"Total Imports: {total_tons:,.2f} tons;")
        insights.append(f"Total Records: {total_records};")
        insights.append(f"Average per Record: {avg_tons:,.2f} tons;")
        if "Consignee State" in df.columns:
            state_agg = df.groupby("Consignee State")["Tons"].sum()
            top_state = state_agg.idxmax()
            top_state_tons = state_agg.max()
            insights.append(f"Top State: {top_state} with {top_state_tons:,.2f} tons;")
        if "Year" in df.columns:
            year_agg = df.groupby("Year")["Tons"].sum()
            top_year = year_agg.idxmax()
            top_year_tons = year_agg.max()
            insights.append(f"Peak Year: {top_year} with {top_year_tons:,.2f} tons.")
        return " ".join(insights)
    except Exception:
        return "Insights not available."

def export_to_csv(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Export selected columns to CSV.
    If include_summary or include_insights is True, prepend a commented summary section.
    """
    data_to_export = df[columns]
    csv_buffer = io.StringIO()
    if include_summary or include_insights:
        csv_buffer.write("# Auto-Generated Report Summary\n")
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
    "Data" for the main report and "Summary" for key metrics and insights.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[columns].to_excel(writer, index=False, sheet_name="Data")
        if include_summary or include_insights:
            summary_df = generate_summary(df)
            insights_text = generate_auto_insights(df) if include_insights else ""
            insights_df = pd.DataFrame({"Insights": [insights_text]})
            summary_combined = pd.concat([summary_df, insights_df], ignore_index=True)
            summary_combined.to_excel(writer, index=False, sheet_name="Summary")
    return output.getvalue()

def export_to_pdf(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Generate a PDF report by converting an HTML string to PDF using pdfkit.
    The report includes a summary section (with metrics and insights) and a data section.
    """
    try:
        import pdfkit
    except ImportError:
        st.error("⚠️ PDF export requires 'pdfkit'. Please install it via pip install pdfkit")
        return None

    html = """
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h2 { color: #2E86C1; }
          h3 { color: #1B4F72; }
          table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          tr:nth-child(even){background-color: #f2f2f2;}
          .insights { font-style: italic; margin-bottom: 20px; }
        </style>
      </head>
      <body>
    """
    html += "<h2>Report Summary</h2>"
    if include_summary:
        summary_df = generate_summary(df)
        html += summary_df.to_html(index=False, border=0)
    if include_insights:
        insights = generate_auto_insights(df)
        html += f'<p class="insights"><strong>Auto Insights:</strong> {insights}</p>'
    
    html += "<h2>Data Report</h2>"
    data_to_export = df[columns]
    html += data_to_export.to_html(index=False, border=0)
    html += "</body></html>"
    try:
        pdf = pdfkit.from_string(html, False)
    except Exception as e:
        st.error(f"🚨 Error generating PDF: {e}")
        return None
    return pdf

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
    
    st.markdown("### Choose Report Format")
    report_format = st.radio("Report Format:", ("CSV", "Excel", "PDF"))
    
    if report_format == "CSV":
        csv_data = export_to_csv(data, selected_columns, include_summary, include_insights)
        st.download_button("📥 Download CSV Report", csv_data, "report.csv", "text/csv")
    elif report_format == "Excel":
        excel_data = export_to_excel(data, selected_columns, include_summary, include_insights)
        st.download_button("📥 Download Excel Report", excel_data, "report.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif report_format == "PDF":
        pdf_data = export_to_pdf(data, selected_columns, include_summary, include_insights)
        if pdf_data is not None:
            st.download_button("📥 Download PDF Report", pdf_data, "report.pdf", "application/pdf")
    
    st.success("✅ Report Generation Ready!")
    
# Additional Option: Overall Dashboard Report
def overall_dashboard_report(data: pd.DataFrame):
    """
    Create an overall interactive dashboard report that aggregates key metrics and charts
    from all areas: market, competitor, supplier, state, and product insights, plus a market forecast.
    """
    st.title("📊 Overall Dashboard Summary Report")
    
    # Data Validation & Preprocessing
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
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Imports (Tons)", f"{total_imports:,.2f}")
    kpi_cols[1].metric("Total Records", total_records)
    kpi_cols[2].metric("Avg Tons per Record", f"{avg_tons:,.2f}")
    # Top state insight
    if "Consignee State" in data.columns:
        state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index()
        top_state_row = state_agg.sort_values("Tons", ascending=False).iloc[0]
        kpi_cols[3].metric("Top State", f"{top_state_row['Consignee State']} ({top_state_row['Tons']:,.2f} Tons)")
    else:
        kpi_cols[3].metric("Top State", "N/A")
    
    st.markdown("---")
    # Market Overview Chart
    st.subheader("Market Overview")
    market_trend = data.groupby("Period")["Tons"].sum().reset_index()
    fig_market = px.line(market_trend, x="Period", y="Tons", title="Overall Market Volume Trend", markers=True)
    st.plotly_chart(fig_market, use_container_width=True)
    
    # Competitor Insights
    st.subheader("Competitor Insights")
    comp_summary = data.groupby("Consignee")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
    fig_comp = px.bar(comp_summary.head(5), x="Consignee", y="Tons", title="Top 5 Competitors by Volume", text_auto=True, color="Tons")
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Supplier Performance
    st.subheader("Supplier Performance")
    supplier_agg = data.groupby("Exporter")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
    fig_supplier = px.bar(supplier_agg.head(5), x="Exporter", y="Tons", title="Top 5 Suppliers by Volume", text_auto=True, color="Tons")
    st.plotly_chart(fig_supplier, use_container_width=True)
    
    # State Insights
    st.subheader("State-Level Insights")
    if "Consignee State" in data.columns:
        state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        fig_state = px.bar(state_agg, x="Consignee State", y="Tons", title="Imports by State", text_auto=True, color="Tons")
        st.plotly_chart(fig_state, use_container_width=True)
    
    # Product Insights
    st.subheader("Product Insights")
    if "Product" in data.columns:
        prod_agg = data.groupby("Product")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        fig_prod = px.pie(prod_agg, names="Product", values="Tons", title="Market Share by Product Category", hole=0.4)
        st.plotly_chart(fig_prod, use_container_width=True)
    
    # Forecasting (Simple Linear Regression)
    st.subheader("Market Forecast")
    market = data.groupby("Period")["Tons"].sum().reset_index().sort_values("Period").reset_index(drop=True)
    if len(market) >= 3:
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
    else:
        st.info("Not enough data to generate a forecast.")
    
    st.success("✅ Overall Dashboard Summary Report Loaded Successfully!")
