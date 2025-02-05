import streamlit as st
import pandas as pd
import plotly.express as px

# ==================== MARKET OVERVIEW DASHBOARD ====================
st.set_page_config(page_title="Market Overview Dashboard", layout="wide")
st.title("📊 Market Overview Dashboard")

# Load the processed data from Core System
@st.cache_data
def load_data():
    """Function to load processed data from Core System."""
    return st.session_state.get("filtered_data", pd.DataFrame())

df = load_data()

if not df.empty:
    st.sidebar.header("📌 Filters")
    selected_state = st.sidebar.multiselect("Select State", options=df["Consignee State"].unique(), default=df["Consignee State"].unique())
    selected_exporter = st.sidebar.multiselect("Select Exporter", options=df["Exporter"].unique(), default=df["Exporter"].unique())
    selected_consignees = st.sidebar.multiselect("Select Consignee", options=df["Consignee"].unique(), default=df["Consignee"].unique())
    selected_months = st.sidebar.multiselect("Select Month", options=df["Month"].unique(), default=df["Month"].unique())

    # Apply Filters
    filtered_df = df[df["Consignee State"].isin(selected_state)]
    filtered_df = filtered_df[filtered_df["Exporter"].isin(selected_exporter)]
    filtered_df = filtered_df[filtered_df["Consignee"].isin(selected_consignees)]
    filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]

    # ==================== KPI METRICS ====================
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Imports (Kgs)", f"{filtered_df['Quantity'].sum():,.0f}")
    col2.metric("Top Importing State", filtered_df.groupby("Consignee State")["Quantity"].sum().idxmax())
    col3.metric("Top Exporter", filtered_df.groupby("Exporter")["Quantity"].sum().idxmax())
    
    # ==================== IMPORT TRENDS ====================
    st.subheader("📈 Monthly Import Trends")
    monthly_trends = filtered_df.groupby("Month")["Quantity"].sum().reset_index()
    fig = px.line(monthly_trends, x="Month", y="Quantity", markers=True, title="Monthly Import Trends")
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== STATE-WISE IMPORT DISTRIBUTION ====================
    st.subheader("🌍 State-Wise Import Distribution")
    state_distribution = filtered_df.groupby("Consignee State")["Quantity"].sum().reset_index()
    fig = px.bar(state_distribution, x="Consignee State", y="Quantity", title="State-Wise Import Distribution", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== EXPORTER PERFORMANCE ====================
    st.subheader("🚢 Exporter Performance")
    exporter_performance = filtered_df.groupby("Exporter")["Quantity"].sum().nlargest(10).reset_index()
    fig = px.bar(exporter_performance, x="Exporter", y="Quantity", title="Top 10 Exporters", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== SMART ALERTS ====================
    st.subheader("⚠️ Smart Alerts")
    alerts = []
    avg_monthly_import = filtered_df.groupby("Month")["Quantity"].sum().mean()
    
    for index, row in monthly_trends.iterrows():
        if row["Quantity"] < 0.7 * avg_monthly_import:
            alerts.append(f"🚨 Drop in imports for {row['Month']} (Below 70% of average)")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ No critical alerts detected!")

    # ==================== EXPORT DATA ====================
    st.sidebar.subheader("📥 Export Data")
    export_format = st.sidebar.radio("Select Format", ["CSV", "Excel"])
    if st.sidebar.button("Download Filtered Data"):
        if export_format == "CSV":
            filtered_df.to_csv("filtered_data.csv", index=False)
            st.sidebar.download_button("Download CSV", open("filtered_data.csv", "rb"), "filtered_data.csv", "text/csv")
        else:
            filtered_df.to_excel("filtered_data.xlsx", index=False)
            st.sidebar.download_button("Download Excel", open("filtered_data.xlsx", "rb"), "filtered_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()
else:
    st.error("No data available. Please upload a file in the Core System.")
