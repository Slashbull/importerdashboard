import streamlit as st
import pandas as pd

# ==================== MARKET OVERVIEW DASHBOARD ====================
st.title("📊 Market Overview Dashboard")

# Function to load processed data from Google Sheets
def load_google_sheets(url):
    """Load data from Google Sheets."""
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(sheet_url)  # Read the Google Sheets data
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return None

# Input for Google Sheets link
gsheet_url = st.text_input("Enter Google Sheets Link (Processed Data)")

if gsheet_url:
    df = load_google_sheets(gsheet_url)  # Load data from Google Sheets

    if df is not None:
        st.write("### Market Overview Statistics")

        # ==================== KPI METRICS ====================
        total_imports = df["Quantity"].sum()
        top_state = df.groupby("Consignee State")["Quantity"].sum().idxmax()
        top_exporter = df.groupby("Exporter")["Quantity"].sum().idxmax()
        top_consignees = df.groupby("Consignee")["Quantity"].sum().nlargest(5)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Imports (Kgs)", f"{total_imports:,.0f}")
        col2.metric("Top Importing State", top_state)
        col3.metric("Top Exporter", top_exporter)

        st.write("### Top 5 Importing Consignees")
        st.dataframe(top_consignees)

        # ==================== IMPORT TRENDS ====================
        st.write("### Monthly Import Trends")
        monthly_trends = df.groupby("Month")["Quantity"].sum().reset_index()
        st.line_chart(monthly_trends, x="Month", y="Quantity")

        # ==================== STATE-WISE IMPORT DISTRIBUTION ====================
        st.write("### State-Wise Import Distribution")
        state_distribution = df.groupby("Consignee State")["Quantity"].sum().reset_index()
        st.bar_chart(state_distribution, x="Consignee State", y="Quantity")

        # ==================== EXPORTER PERFORMANCE ====================
        st.write("### Exporter Performance")
        exporter_performance = df.groupby("Exporter")["Quantity"].sum().nlargest(10).reset_index()
        st.bar_chart(exporter_performance, x="Exporter", y="Quantity")

        # ==================== SMART ALERTS ====================
        st.write("### Smart Alerts")
        alerts = []
        avg_monthly_import = df.groupby("Month")["Quantity"].sum().mean()

        for index, row in monthly_trends.iterrows():
            if row["Quantity"] < 0.7 * avg_monthly_import:
                alerts.append(f"🚨 Drop in imports for {row['Month']} (Below 70% of average)")

        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("✅ No critical alerts detected!")

        # ==================== LOGOUT ====================
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.experimental_rerun()

    else:
        st.error("Failed to load the data from the provided Google Sheets link.")
else:
    st.info("Please enter the Google Sheets link containing the processed data.")
