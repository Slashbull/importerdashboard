import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def market_overview_dashboard(data: pd.DataFrame):
    st.title("📊 Market Overview Dashboard")
    
    # ---------------------------
    # Data & Column Validation
    # ---------------------------
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = [
        "SR NO.", "Job No.", "Consignee", "Exporter",
        "Mark", "Tons", "Month", "Year", "Consignee State"
    ]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert Tons to numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # ---------------------------
    # Create and Order the "Period" Column
    # ---------------------------
    if "Period" not in data.columns:
        # Convert Month and Year into a datetime column
        try:
            data["Period_dt"] = data.apply(
                lambda row: datetime.strptime(f"{row['Month']} {row['Year']}", "%b %Y"), axis=1
            )
        except Exception as e:
            st.error("Error parsing 'Month' and 'Year'. Please ensure they are in 'Mon' and numeric formats.")
            return
        
        # Format the datetime into a string (e.g., "Jan-2024")
        data["Period"] = data["Period_dt"].dt.strftime("%b-%Y")
        # Create an ordered categorical variable for proper sorting
        sorted_periods = sorted(data["Period_dt"].dropna().unique())
        period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
        data["Period"] = pd.Categorical(data["Period"], categories=period_labels, ordered=True)
    
    # ---------------------------
    # Date Range Filtering
    # ---------------------------
    # Use the datetime column "Period_dt" for filtering
    min_date = data["Period_dt"].min().date()
    max_date = data["Period_dt"].max().date()
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    if len(date_range) == 2:
        start_date, end_date = date_range
        data = data[(data["Period_dt"].dt.date >= start_date) & (data["Period_dt"].dt.date <= end_date)]
    
    # ---------------------------
    # KPI Calculations
    # ---------------------------
    total_imports = data["Tons"].sum()
    unique_consignees = data["Consignee"].nunique()
    unique_exporters = data["Exporter"].nunique()
    avg_imports = total_imports / unique_consignees if unique_consignees > 0 else 0
    
    # Calculate Month-over-Month (MoM) Growth using the last two ordered periods
    unique_periods = list(data["Period"].cat.categories)
    if len(unique_periods) >= 2:
        last_period = unique_periods[-1]
        second_last_period = unique_periods[-2]
        tons_last = data[data["Period"] == last_period]["Tons"].sum()
        tons_second_last = data[data["Period"] == second_last_period]["Tons"].sum()
        mom_growth = ((tons_last - tons_second_last) / tons_second_last * 100) if tons_second_last else 0
    else:
        mom_growth = 0

    # ---------------------------
    # Tabbed Layout: Summary, Trends, Breakdown
    # ---------------------------
    tab_summary, tab_trends, tab_breakdown = st.tabs(["Summary", "Trends", "Breakdown"])

    # ---------------------------
    # Tab 1: Summary – KPIs & Market Share Overview
    # ---------------------------
    with tab_summary:
        st.subheader("Key Performance Indicators")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Imports (Tons)", f"{total_imports:,.2f}")
        col2.metric("Unique Consignees", unique_consignees)
        col3.metric("Unique Exporters", unique_exporters)
        col4.metric("Avg Tons per Consignee", f"{avg_imports:,.2f}")
        col5.metric("MoM Growth (%)", f"{mom_growth:,.2f}")
        
        st.markdown("---")
        st.subheader("Market Share Overview")
        # Calculate percentage share for hover details
        cons_share = data.groupby("Consignee")["Tons"].sum().reset_index()
        total = cons_share["Tons"].sum()
        cons_share["Percentage"] = (cons_share["Tons"] / total) * 100
        fig_donut = px.pie(
            cons_share,
            names="Consignee",
            values="Tons",
            title="Market Share by Consignee",
            hole=0.4,
            hover_data={"Percentage":":.2f"}
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ---------------------------
    # Tab 2: Trends – Time Series Analysis
    # ---------------------------
    with tab_trends:
        st.subheader("Overall Monthly Trends")
        monthly_trends = data.groupby("Period")["Tons"].sum().reset_index()
        # Convert Period to string for the x-axis
        monthly_trends["Period_str"] = monthly_trends["Period"].astype(str)
        fig_line = px.line(
            monthly_trends,
            x="Period_str",
            y="Tons",
            title="Monthly Import Trends",
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        if data["Year"].nunique() > 1:
            st.markdown("#### Trends by Year")
            yearly_trends = data.groupby(["Year", "Month"])["Tons"].sum().reset_index()
            # Sort months using a predefined order
            month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                           "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
            yearly_trends["Month_Order"] = yearly_trends["Month"].map(month_order)
            yearly_trends = yearly_trends.sort_values("Month_Order")
            fig_yearly = px.line(
                yearly_trends,
                x="Month",
                y="Tons",
                color="Year",
                title="Monthly Trends by Year",
                markers=True
            )
            st.plotly_chart(fig_yearly, use_container_width=True)

    # ---------------------------
    # Tab 3: Breakdown – Top Entities & Importer/Exporter Contribution
    # ---------------------------
    with tab_breakdown:
        st.subheader("Top Entities")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Top 5 Competitors (Consignees)**")
            top_consignees = data.groupby("Consignee")["Tons"].sum().nlargest(5).reset_index()
            fig_top_comp = px.bar(
                top_consignees,
                x="Consignee",
                y="Tons",
                title="Top 5 Competitors",
                labels={"Tons": "Total Tons"},
                text_auto=True,
                color="Tons"
            )
            st.plotly_chart(fig_top_comp, use_container_width=True)
        with colB:
            st.markdown("**Top 5 Exporters**")
            top_exporters = data.groupby("Exporter")["Tons"].sum().nlargest(5).reset_index()
            fig_top_exp = px.bar(
                top_exporters,
                x="Exporter",
                y="Tons",
                title="Top 5 Exporters",
                labels={"Tons": "Total Tons"},
                text_auto=True,
                color="Tons"
            )
            st.plotly_chart(fig_top_exp, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Importer/Exporter Contribution")
        st.markdown(
            "This treemap provides a hierarchical view of how each importer (Consignee) is connected with various exporters. "
            "Segment size represents the total Tons."
        )
        contribution = data.groupby(["Consignee", "Exporter"])["Tons"].sum().reset_index()
        fig_treemap = px.treemap(
            contribution,
            path=["Consignee", "Exporter"],
            values="Tons",
            title="Importer/Exporter Contribution Treemap",
            color="Tons",
            color_continuous_scale="Blues",
            hover_data={"Tons": True}
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        
        st.markdown("#### Detailed Contribution Table")
        simple_table = contribution.sort_values("Tons", ascending=False)
        st.dataframe(simple_table)

    st.success("✅ Market Overview Dashboard Loaded Successfully!")
