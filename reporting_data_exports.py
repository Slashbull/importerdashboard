import streamlit as st
import pandas as pd
import io

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
    summary_df = pd.DataFrame(summary_data)
    return summary_df

def generate_auto_insights(df: pd.DataFrame) -> str:
    """
    Generate an automatic textual summary of key insights from the data.
    For example:
      - Total imports and average per record.
      - The state with the highest total imports.
      - The year with the highest imports (if available).
    
    Returns:
        A string containing the auto-generated insights.
    """
    try:
        total_tons = df["Tons"].sum()
        total_records = df.shape[0]
        avg_tons = total_tons / total_records if total_records > 0 else 0

        insights = []
        insights.append(f"Total Imports (Tons): {total_tons:,.2f}.")
        insights.append(f"Total Records: {total_records}.")
        insights.append(f"Average Tons per Record: {avg_tons:,.2f}.")

        if "Consignee State" in df.columns:
            state_agg = df.groupby("Consignee State")["Tons"].sum()
            top_state = state_agg.idxmax()
            top_state_tons = state_agg.max()
            insights.append(f"The state with the highest imports is {top_state} with {top_state_tons:,.2f} tons.")

        if "Year" in df.columns:
            year_agg = df.groupby("Year")["Tons"].sum()
            top_year = year_agg.idxmax()
            top_year_tons = year_agg.max()
            insights.append(f"In {top_year}, the total imports reached {top_year_tons:,.2f} tons.")

        # Join all insights into one summary string.
        return " ".join(insights)
    except Exception as e:
        return "Could not generate automatic insights due to an error."

def export_to_csv(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Export selected columns to CSV. Optionally, prepend summary metrics and auto insights.
    
    For CSV, insights and summary are prepended as commented lines.
    """
    data_to_export = df[columns]
    csv_buffer = io.StringIO()
    
    if include_summary or include_insights:
        csv_buffer.write("# Auto-Generated Report Summary\n")
        if include_summary:
            summary_df = generate_summary(df)
            # Write summary rows with a comment marker.
            for _, row in summary_df.iterrows():
                csv_buffer.write(f"# {row['Metric']}: {row['Value']}\n")
        if include_insights:
            insights = generate_auto_insights(df)
            csv_buffer.write(f"# Insights: {insights}\n")
        csv_buffer.write("\n")
    
    data_to_export.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")

def export_to_excel(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Export selected columns to an Excel file.
    Creates two sheets: "Data" and "Summary".
    The "Summary" sheet includes both the summary table and the auto-generated insights.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Write the main data.
        df[columns].to_excel(writer, index=False, sheet_name="Data")
        if include_summary or include_insights:
            summary_df = generate_summary(df)
            # Create a DataFrame for insights.
            insights = generate_auto_insights(df)
            insights_df = pd.DataFrame({"Insights": [insights]})
            # Write summary and insights in one sheet.
            summary_combined = pd.concat([summary_df, insights_df], ignore_index=True)
            summary_combined.to_excel(writer, index=False, sheet_name="Summary")
    return output.getvalue()

def export_to_pdf(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Generate a PDF report by converting an HTML string to PDF using pdfkit.
    The report includes a summary section (with metrics and auto-generated insights) and a data report.
    """
    try:
        import pdfkit
    except ImportError:
        st.error("⚠️ PDF export requires 'pdfkit'. Please install it via pip install pdfkit")
        return None

    # Build HTML content for the report.
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
    # Add Summary Section.
    html += "<h2>Report Summary</h2>"
    if include_summary:
        summary_df = generate_summary(df)
        html += summary_df.to_html(index=False, border=0)
    if include_insights:
        insights = generate_auto_insights(df)
        html += f'<p class="insights"><strong>Auto Insights:</strong> {insights}</p>'
    
    # Add Data Report Section.
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
