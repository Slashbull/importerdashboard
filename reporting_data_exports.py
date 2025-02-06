import streamlit as st
import pandas as pd

def reporting_data_exports(data: pd.DataFrame):
    st.title("📄 Reporting & Data Exports Dashboard")

    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    st.markdown("### 📥 Generate Reports")
    report_format = st.radio("Choose Report Format:", ("CSV", "Excel", "PDF"))
    
    if report_format == "CSV":
        csv_data = data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV Report", csv_data, "report.csv", "text/csv")
    
    elif report_format == "Excel":
        excel_file = "report.xlsx"
        data.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as file:
            st.download_button("📥 Download Excel Report", file, excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    elif report_format == "PDF":
        try:
            import pdfkit
            pdf_file = "report.pdf"
            data.to_html("report.html")
            pdfkit.from_file("report.html", pdf_file)
            with open(pdf_file, "rb") as file:
                st.download_button("📥 Download PDF Report", file, pdf_file, "application/pdf")
        except ImportError:
            st.error("⚠️ PDF export requires 'pdfkit' package. Install it via pip.")
    
    st.success("✅ Report Generation Ready!")
