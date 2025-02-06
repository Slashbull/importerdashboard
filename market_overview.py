import streamlit as st
import pandas as pd
import plotly.express as px

def market_overview_dashboard(data: pd.DataFrame):
    st.title("📊 Market Overview Dashboard")
    
    # Check that data exists and required columns are present
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

    # Ensure the Tons column is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Define a month order dictionary for proper sorting
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    # Create a tabbed layout with six tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Key Metrics", "Top Entities", "Monthly Trends", "Market Share", "Growth Analysis", "Importer/Exporter Contribution"
    ])
    
    # ---------------------------
    # Tab 1: Key Metrics
    # ---------------------------
    with tab1:
        st.subheader("Key Metrics")
        total_imports = data["Tons"].sum()
        unique_consignees = data["Consignee"].nunique()
        unique_exporters = data["Exporter"].nunique()
        avg_imports_per_consignee = total_imports / unique_consignees if unique_consignees > 0 else 0

        # Calculate Month-over-Month (MoM) Growth
        monthly_data = data.groupby("Month")["Tons"].sum().reset_index()
        monthly_data["Month_Order"] = monthly_data["Month"].map(month_order)
        monthly_data = monthly_data.sort_values("Month_Order")
        if monthly_data.shape[0] >= 2 and monthly_data["Tons"].iloc[-2] != 0:
            recent_growth = ((monthly_data["Tons"].iloc[-1] - monthly_data["Tons"].iloc[-2]) /
                             monthly_data["Tons"].iloc[-2]) * 100
        else:
            recent_growth = 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Imports (Tons)", f"{total_imports:,.2f}")
        col2.metric("Unique Consignees", unique_consignees)
        col3.metric("Unique Exporters", unique_exporters)
        col4.metric("Avg Tons per Consignee", f"{avg_imports_per_consignee:,.2f}")
        col5.metric("MoM Growth (%)", f"{recent_growth:,.2f}")

    # ---------------------------
    # Tab 2: Top Entities
    # ---------------------------
    with tab2:
        st.subheader("Top Entities")
        # Top Competitors (Consignees)
        st.markdown("#### Top Competitors by Tons")
        top_consignees = data.groupby("Consignee")["Tons"].sum().nlargest(5).reset_index()
        fig1 = px.bar(
            top_consignees,
            x="Consignee",
            y="Tons",
            title="Top 5 Competitors",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Top Exporters
        st.markdown("#### Top Exporters by Tons")
        top_exporters = data.groupby("Exporter")["Tons"].sum().nlargest(5).reset_index()
        fig2 = px.bar(
            top_exporters,
            x="Exporter",
            y="Tons",
            title="Top 5 Exporters",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------
    # Tab 3: Monthly Trends
    # ---------------------------
    with tab3:
        st.subheader("Monthly Import Trends")
        monthly_trends = data.groupby("Month")["Tons"].sum().reset_index()
        monthly_trends["Month_Order"] = monthly_trends["Month"].map(month_order)
        monthly_trends = monthly_trends.sort_values("Month_Order")
        fig3 = px.line(
            monthly_trends,
            x="Month",
            y="Tons",
            title="Overall Monthly Trends",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        if data["Year"].nunique() > 1:
            st.markdown("#### Monthly Trends by Year")
            yearly_trends = data.groupby(["Year", "Month"])["Tons"].sum().reset_index()
            yearly_trends["Month_Order"] = yearly_trends["Month"].map(month_order)
            yearly_trends = yearly_trends.sort_values("Month_Order")
            fig_year = px.line(
                yearly_trends,
                x="Month",
                y="Tons",
                color="Year",
                title="Monthly Trends by Year",
                markers=True
            )
            st.plotly_chart(fig_year, use_container_width=True)

    # ---------------------------
    # Tab 4: Market Share
    # ---------------------------
    with tab4:
        st.subheader("Market Share Analysis")
        st.markdown("#### Market Share by Consignee")
        consignee_share = data.groupby("Consignee")["Tons"].sum().reset_index()
        fig4 = px.pie(
            consignee_share,
            names="Consignee",
            values="Tons",
            title="Market Share by Consignee"
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown("#### Market Share by Exporter")
        exporter_share = data.groupby("Exporter")["Tons"].sum().reset_index()
        fig5 = px.pie(
            exporter_share,
            names="Exporter",
            values="Tons",
            title="Market Share by Exporter"
        )
        st.plotly_chart(fig5, use_container_width=True)

    # ---------------------------
    # Tab 5: Growth Analysis
    # ---------------------------
    with tab5:
        st.subheader("Growth Analysis by Period")
        # Create a Period column by combining Month and Year if not already present
        if "Period" not in data.columns:
            data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
        period_totals = data.groupby("Period")["Tons"].sum().reset_index()
        period_totals = period_totals.sort_values("Period")  # Adjust sorting logic if needed
        period_totals["Percentage Change (%)"] = period_totals["Tons"].pct_change() * 100
        st.dataframe(period_totals)
        
        st.markdown("#### Import Trend Over Periods")
        fig6 = px.line(
            period_totals,
            x="Period",
            y="Tons",
            title="Import Trend by Period",
            markers=True
        )
        st.plotly_chart(fig6, use_container_width=True)

    # ---------------------------
    # Tab 6: Importer/Exporter Contribution
    # ---------------------------
    with tab6:
        st.subheader("Importer/Exporter Contribution")
        st.markdown("This view shows, for each importer (Consignee), the contribution from each exporter.")
        # Group by Consignee and Exporter, summing Tons
        contribution = data.groupby(["Consignee", "Exporter"])["Tons"].sum().reset_index()
        # Create a stacked bar chart: x-axis is Consignee, y-axis is Tons, colored by Exporter.
        fig_contrib = px.bar(
            contribution,
            x="Consignee",
            y="Tons",
            color="Exporter",
            title="Stacked Contribution by Importer (Consignee)",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig_contrib, use_container_width=True)
        
        # Optionally, show a pivot table as a heatmap
        pivot_table = contribution.pivot(index="Consignee", columns="Exporter", values="Tons").fillna(0)
        st.markdown("#### Contribution Heatmap Data")
        st.dataframe(pivot_table)

    st.success("✅ Market Overview Dashboard Loaded Successfully!")
