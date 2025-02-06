import streamlit as st
import pandas as pd
import io

def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary DataFrame with key metrics.
    Adjust or add additional metrics as needed.
    """
    total_tons = df["Tons"].sum()
    total_records = df.shape[0]
    avg_tons = total_tons / total_records if total_records > 0 else 0

    summary_data = {
        "Metric": ["Total Tons", "Total Records", "Average Tons per Record"],
        "Value": [f"{total_tons:,.2f}", total_records, f"{avg_tons:,.2f}"]
    }
    summary_df = pd.DataFrame(summary_data)
    return summary_df

def export_to_csv(df: pd.DataFrame, columns: list, include_summary: bool) -> bytes:
    """
    Generate a CSV file from the DataFrame with selected columns.
    If include_summary is True, prepend summary information to the CSV.
    """
    # Filter columns
    data_to_export = df[columns]
    csv_buffer = io.StringIO()

    if include_summary:
        summary_df = generate_summary(df)
        # Write summary first
        summary_df.to_csv(csv_buffer, index=False)
        csv_buffer.write("\n")  # Separate summary and data with an empty line

    # Write the main data
    data_to_export.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")

def export_to_excel(df: pd.DataFrame, columns: list, include_summary: bool) -> bytes:
    """
    Generate an Excel file with one sheet for data and, if selected, one for summary.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[columns].to_excel(writer, index=False, sheet_name="Data")
        if include_summary:
            summary_df = generate_summary(df)
            summary_df.to_excel(writer, index=False, sheet_name="Summary")
        writer.save()
    processed_data = output.getvalue()
    return processed_data

def export_to_pdf(df: pd.DataFrame, columns: list, include_summary: bool) -> bytes:
    """
    Generate a PDF report by converting an HTML string to PDF using pdfkit.
    Note: Ensure that pdfkit and wkhtmltopdf are installed and properly configured.
    """
    try:
        import pdfkit
    except ImportError:
        st.error("⚠️ PDF export requires 'pdfkit' package. Install it via pip.")
        return None

    # Prepare HTML content
    html = "<html><head><meta charset='utf-8'><style>"
    html += """
    body { font-family: Arial, sans-serif; margin: 20px; }
    h2 { color: #2E86C1; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    tr:nth-child(even){background-color: #f2f2f2;}
    </style></head><body>
    """
    html += "<h2>Report Summary</h2>"
    if include_summary:
        summary_df = generate_summary(df)
        html += summary_df.to_html(index=False, border=0)
    html += "<h2>Data Report</h2>"
    data_to_export = df[columns]
    html += data_to_export.to_html(index=False, border=0)
    html += "</body></html>"

    # Convert HTML to PDF using pdfkit
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

    st.markdown("### 📥 Report Options")
    
    # Let the user choose which columns to include in the report.
    all_columns = list(data.columns)
    selected_columns = st.multiselect("Select Columns to Include:", options=all_columns, default=all_columns)
    
    # Option to include summary metrics
    include_summary = st.checkbox("Include Summary Metrics", value=False)
    
    st.markdown("### 📥 Generate Reports")
    report_format = st.radio("Choose Report Format:", ("CSV", "Excel", "PDF"))
    
    if report_format == "CSV":
        csv_data = export_to_csv(data, selected_columns, include_summary)
        st.download_button("📥 Download CSV Report", csv_data, "report.csv", "text/csv")
    
    elif report_format == "Excel":
        excel_data = export_to_excel(data, selected_columns, include_summary)
        st.download_button("📥 Download Excel Report", excel_data, "report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    elif report_format == "PDF":
        pdf_data = export_to_pdf(data, selected_columns, include_summary)
        if pdf_data is not None:
            st.download_button("📥 Download PDF Report", pdf_data, "report.pdf", "application/pdf")
    
    st.success("✅ Report Generation Ready!")
