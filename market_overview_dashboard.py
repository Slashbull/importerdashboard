import streamlit as st
import pandas as pd
import plotly.express as px

# ==================== MARKET OVERVIEW DASHBOARD ====================
st.title("📊 Market Overview Dashboard")

# Load data from Core System Foundation
@st.cache_data
def load_data():
    return st.session_state.get("filtered_data", pd.DataFrame())

df = load_data()

if not df.empty:
    # ==================== FILTER SYSTEM ====================
    st.sidebar.header("📌 Advanced Filters")
    selected_state = st.sidebar.multiselect("Select State", options=df["Consignee State"].unique(), default=df["Consignee State"].unique())
    selected_exporter = st.sidebar.multiselect("Select Exporter", options=df["Exporter"].unique(), default=df["Exporter"].unique())
    selected_consignees = st.sidebar.multiselect("Select Consignee", options=df["Consignee"].unique(), default=df["Consignee"].unique())
    selected_months = st.sidebar.multiselect("Select Month", options=["All"] + list(df["Month"].unique()), default=["All"])
    selected_years = st.sidebar.multiselect("Select Year", options=["All"] + list(df["Year"].unique()), default=["All"]) 
    unit_toggle = st.sidebar.radio("Select Unit", ["Kgs", "Tons"], horizontal=True)

    # Apply Filters
    df = df[df["Consignee State"].isin(selected_state)]
    df = df[df["Exporter"].isin(selected_exporter)]
    df = df[df["Consignee"].isin(selected_consignees)]
    if "All" not in selected_months:
        df = df[df["Month"].isin(selected_months)]
    if "All" not in selected_years:
        df = df[df["Year"].isin(selected_years)]

    # Adjust for Unit Toggle
    df["Quantity_Display"] = df["Quantity_Tons"] if unit_toggle == "Tons" else df["Quantity"]

    # ==================== KPI METRICS ====================
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Imports", f"{df['Quantity_Display'].sum():,.0f} {unit_toggle}" if 'Quantity_Display' in df.columns else "Data Unavailable")
    col2.metric("Top Importing State", df.groupby("Consignee State")["Quantity_Display"].sum().idxmax())
    col3.metric("Top Exporter", df.groupby("Exporter")["Quantity_Display"].sum().idxmax())
    
    # ==================== IMPORT TRENDS ====================
    st.subheader("📈 Monthly Import Trends")
    monthly_trends = df.groupby("Month")["Quantity_Display"].sum().reset_index()
    fig = px.line(monthly_trends, x="Month", y="Quantity_Display", markers=True, title="Monthly Import Trends")
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== STATE-WISE IMPORT DISTRIBUTION ====================
    st.subheader("🌍 State-Wise Import Distribution")
    state_distribution = df.groupby("Consignee State")["Quantity_Display"].sum().reset_index()
    fig = px.bar(state_distribution, x="Consignee State", y="Quantity_Display", title="State-Wise Import Distribution", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== EXPORTER PERFORMANCE ====================
    st.subheader("🚢 Exporter Performance")
    exporter_performance = df.groupby("Exporter")["Quantity_Display"].sum().nlargest(10).reset_index()
    fig = px.bar(exporter_performance, x="Exporter", y="Quantity_Display", title="Top 10 Exporters", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== SMART ALERTS ====================
    st.subheader("⚠️ Smart Alerts")
    alerts = []
    avg_monthly_import = df.groupby("Month")["Quantity_Display"].sum().mean()
    
    for index, row in monthly_trends.iterrows():
        if row["Quantity_Display"] < 0.7 * avg_monthly_import:
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
            df.to_csv("filtered_data.csv", index=False)
            st.sidebar.download_button("Download CSV", open("filtered_data.csv", "rb"), "filtered_data.csv", "text/csv")
        else:
            df.to_excel("filtered_data.xlsx", index=False)
            st.sidebar.download_button("Download Excel", open("filtered_data.xlsx", "rb"), "filtered_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
else:
    st.error("No data available. Please upload a file in the Core System.")
