import streamlit as st
import pandas as pd
import plotly.express as px

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

    # Convert Tons to numeric (if not already)
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Define month ordering for proper sorting
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    
    # Create a "Period" column (Month-Year) if not already present
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # ---------------------------
    # Tabbed Layout: Summary, Trends, and Breakdown
    # ---------------------------
    tab_summary, tab_trends, tab_breakdown = st.tabs(["Summary", "Trends", "Breakdown"])

    # ---------------------------
    # Tab 1: Summary – Key Metrics & Overview
    # ---------------------------
    with tab_summary:
        st.subheader("Key Performance Indicators")
        total_imports = data["Tons"].sum()
        unique_consignees = data["Consignee"].nunique()
        unique_exporters = data["Exporter"].nunique()
        avg_imports = total_imports / unique_consignees if unique_consignees > 0 else 0
        
        # Calculate Month-over-Month (MoM) Growth
        monthly_data = data.groupby("Month")["Tons"].sum().reset_index()
        monthly_data["Month_Order"] = monthly_data["Month"].map(month_order)
        monthly_data = monthly_data.sort_values("Month_Order")
        if monthly_data.shape[0] >= 2 and monthly_data["Tons"].iloc[-2] != 0:
            mom_growth = ((monthly_data["Tons"].iloc[-1] - monthly_data["Tons"].iloc[-2]) /
                          monthly_data["Tons"].iloc[-2]) * 100
        else:
            mom_growth = 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Imports (Tons)", f"{total_imports:,.2f}")
        col2.metric("Unique Consignees", unique_consignees)
        col3.metric("Unique Exporters", unique_exporters)
        col4.metric("Avg Tons per Consignee", f"{avg_imports:,.2f}")
        col5.metric("MoM Growth (%)", f"{mom_growth:,.2f}")

        st.markdown("---")
        st.subheader("Market Share Overview")
        # Donut chart for Consignee Market Share
        cons_share = data.groupby("Consignee")["Tons"].sum().reset_index()
        fig_donut = px.pie(
            cons_share, names="Consignee", values="Tons",
            title="Market Share by Consignee", hole=0.4
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ---------------------------
    # Tab 2: Trends – Time Series Analysis
    # ---------------------------
    with tab_trends:
        st.subheader("Overall Monthly Trends")
        monthly_trends = data.groupby("Month")["Tons"].sum().reset_index()
        monthly_trends["Month_Order"] = monthly_trends["Month"].map(month_order)
        monthly_trends = monthly_trends.sort_values("Month_Order")
        fig_line = px.line(
            monthly_trends,
            x="Month", y="Tons",
            title="Monthly Import Trends",
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        if data["Year"].nunique() > 1:
            st.markdown("#### Trends by Year")
            yearly_trends = data.groupby(["Year", "Month"])["Tons"].sum().reset_index()
            yearly_trends["Month_Order"] = yearly_trends["Month"].map(month_order)
            yearly_trends = yearly_trends.sort_values("Month_Order")
            fig_yearly = px.line(
                yearly_trends,
                x="Month", y="Tons",
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
                x="Consignee", y="Tons",
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
                x="Exporter", y="Tons",
                title="Top 5 Exporters",
                labels={"Tons": "Total Tons"},
                text_auto=True,
                color="Tons"
            )
            st.plotly_chart(fig_top_exp, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Importer/Exporter Contribution")
        st.markdown("This sunburst chart shows, in a hierarchical way, how each importer (Consignee) is connected with various exporters, with segment size representing the Tons.")
        # Group data for the sunburst chart
        contribution = data.groupby(["Consignee", "Exporter"])["Tons"].sum().reset_index()
        fig_sunburst = px.sunburst(
            contribution,
            path=["Consignee", "Exporter"],
            values="Tons",
            title="Importer/Exporter Contribution",
            color="Tons",
            color_continuous_scale="Blues",
            hover_data={"Tons": True}
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
        
        st.markdown("#### Detailed Contribution Data")
        pivot_table = contribution.pivot(index="Consignee", columns="Exporter", values="Tons").fillna(0)
        st.dataframe(pivot_table)

    st.success("✅ Market Overview Dashboard Loaded Successfully!")
