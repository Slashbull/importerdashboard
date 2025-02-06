import streamlit as st
import pandas as pd
import plotly.express as px

def state_level_market_insights(data: pd.DataFrame):
    st.title("🌍 State-Level Market Insights Dashboard")
    
    # ---------------------------
    # Data Validation
    # ---------------------------
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee State", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert Tons to numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create a "Period" column if not present (Month-Year)
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Define month ordering for proper sorting
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    
    # ---------------------------
    # Tabbed Layout: Overview, Trends, Growth Analysis, Detailed Analysis
    # ---------------------------
    tab_overview, tab_trends, tab_growth, tab_details = st.tabs([
        "Overview", "Trends", "Growth Analysis", "Detailed Analysis"
    ])

    # ---------------------------
    # Tab 1: Overview – Key Metrics & Top States
    # ---------------------------
    with tab_overview:
        st.subheader("Key Performance Indicators")
        state_agg = data.groupby("Consignee State")["Tons"].sum().reset_index()
        total_imports = state_agg["Tons"].sum()
        num_states = state_agg["Consignee State"].nunique()
        avg_imports = total_imports / num_states if num_states > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Imports (Tons)", f"{total_imports:,.2f}")
        col2.metric("Unique States", num_states)
        col3.metric("Avg Tons per State", f"{avg_imports:,.2f}")

        st.markdown("---")
        st.subheader("Top Importing States")
        top_states = state_agg.sort_values(by="Tons", ascending=False).head(5)
        fig_bar = px.bar(
            top_states,
            x="Consignee State",
            y="Tons",
            title="Top 5 States by Tons",
            labels={"Tons": "Total Tons"},
            text_auto=True,
            color="Tons"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------------------
    # Tab 2: Trends – Time Series Analysis by State
    # ---------------------------
    with tab_trends:
        st.subheader("Overall Monthly Trends by State")
        trends_df = data.groupby(["Consignee State", "Period"])["Tons"].sum().reset_index()
        fig_trends = px.line(
            trends_df,
            x="Period",
            y="Tons",
            color="Consignee State",
            title="Monthly Trends by State",
            markers=True
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Select States for Detailed Trend Analysis")
        all_states = sorted(data["Consignee State"].dropna().unique().tolist())
        selected_states = st.multiselect("States", options=all_states, default=all_states[:3])
        if selected_states:
            detailed_trends = data[data["Consignee State"].isin(selected_states)]
            detailed_df = detailed_trends.groupby(["Consignee State", "Period"])["Tons"].sum().reset_index()
            fig_detail = px.line(
                detailed_df,
                x="Period",
                y="Tons",
                color="Consignee State",
                title="Detailed Trends for Selected States",
                markers=True
            )
            st.plotly_chart(fig_detail, use_container_width=True)
        else:
            st.info("Please select at least one state for detailed analysis.")

    # ---------------------------
    # Tab 3: Growth Analysis – Period-over-Period Change
    # ---------------------------
    with tab_growth:
        st.subheader("State-Level Growth Analysis")
        # Create a pivot table: rows = Consignee State, columns = Period, values = Tons
        pivot_table = data.pivot_table(
            index="Consignee State",
            columns="Period",
            values="Tons",
            aggfunc="sum",
            fill_value=0
        )
        # Compute percentage changes for each state across periods
        growth_pct = pivot_table.pct_change(axis=1) * 100
        growth_pct = growth_pct.round(2)
        st.markdown("#### Period-over-Period Percentage Change (%)")
        st.dataframe(growth_pct)
        
        # Additionally, show average growth per state as a bar chart
        avg_growth = growth_pct.mean(axis=1).reset_index()
        avg_growth.columns = ["Consignee State", "Average Growth (%)"]
        fig_growth = px.bar(
            avg_growth,
            x="Consignee State",
            y="Average Growth (%)",
            title="Average Period-over-Period Growth by State",
            text_auto=True,
            color="Average Growth (%)"
        )
        st.plotly_chart(fig_growth, use_container_width=True)

    # ---------------------------
    # Tab 4: Detailed Analysis – Pivot Table View
    # ---------------------------
    with tab_details:
        st.subheader("Detailed State-Level Data")
        detailed_pivot = data.pivot_table(
            index="Consignee State",
            columns="Period",
            values="Tons",
            aggfunc="sum",
            fill_value=0
        )
        st.dataframe(detailed_pivot)
        
        st.markdown("#### Summary Table by State")
        summary_table = data.groupby("Consignee State")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        st.dataframe(summary_table)

    st.success("✅ State-Level Market Insights Dashboard Loaded Successfully!")
