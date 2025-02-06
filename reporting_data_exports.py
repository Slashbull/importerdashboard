import streamlit as st
import pandas as pd

# ---- Reporting & Data Exports Dashboard ---- #
def reporting_data_exports():
    st.title("📄 Reporting & Data Exports Dashboard")

    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    df = st.session_state["uploaded_data"]

    st.markdown("### 📥 Generate Reports")
    report_format = st.radio("Choose Report Format:", ("CSV", "Excel", "PDF"))
    
    if report_format == "CSV":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV Report", csv, "report.csv", "text/csv")
    
    elif report_format == "Excel":
        excel_file = "report.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as file:
            st.download_button("📥 Download Excel Report", file, excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    elif report_format == "PDF":
        try:
            import pdfkit
            pdf_file = "report.pdf"
            df.to_html("report.html")
            pdfkit.from_file("report.html", pdf_file)
            with open(pdf_file, "rb") as file:
                st.download_button("📥 Download PDF Report", file, pdf_file, "application/pdf")
        except ImportError:
            st.error("⚠️ PDF export requires 'pdfkit' package. Install using: pip install pdfkit")

    st.success("✅ Report Generation Ready!")
