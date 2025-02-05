import streamlit as st
import pandas as pd

# ==================== MARKET OVERVIEW DASHBOARD ====================
st.title("📊 Market Overview Dashboard")

# Load the processed data from Core System
@st.cache_data
def load_data():
    """Function to load processed data from Core System."""
    return pd.read_csv("processed_data.csv")  # Ensure processed_data.csv is updated from Core System

df = load_data()

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

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()
else:
    st.error("No data available. Please upload a file in the Core System.")
