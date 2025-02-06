import streamlit as st
import pandas as pd
import plotly.express as px

def state_level_market_insights(data: pd.DataFrame):
    st.title("🌍 State-Level Market Insights Dashboard")
    
    # Check for required data and columns
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return
    
    required_columns = ["Consignee State", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure the Tons column is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Define a month ordering dictionary for proper sorting
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    # Create a tabbed layout for different sections of the dashboard
    tab_overview, tab_trends, tab_growth = st.tabs([
        "Overview", "Trends", "Growth Analysis"
    ])

    # ------------------------------------------------------
    # Tab 1: Overview – Key Metrics and Top Importing States
    # ------------------------------------------------------
    with tab_overview:
        st.subheader("Key Metrics")
        # Group by state and calculate total imports per state
        state_totals = data.groupby("Consignee State")["Tons"].sum().reset_index()
        total_imports_all = state_totals["Tons"].sum()
        total_states = state_totals["Consignee State"].nunique()
        avg_imports_state = total_imports_all / total_states if total_states else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Imports (Tons)", f"{total_imports_all:,.2f}")
        col2.metric("Total States", total_states)
        col3.metric("Avg Tons per State", f"{avg_imports_state:,.2f}")

        st.markdown("### Top Importing States")
        # Sort and show top 5 states by total imports
        top_states = state_totals.sort_values(by="Tons", ascending=False).head(5)
        fig_overview = px.bar(
            top_states,
            x="Consignee State",
            y="Tons",
            title="Top 5 Importing States",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig_overview, use_container_width=True)
        st.write("")  # Spacer

    # ------------------------------------------------------
    # Tab 2: Trends – Monthly Trends by State
    # ------------------------------------------------------
    with tab_trends:
        st.subheader("Monthly Import Trends by State")
        # Create a Period column for trend analysis (Month-Year)
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
        
        # Allow user to select one or more states for detailed trend analysis
        all_states = sorted(data["Consignee State"].dropna().unique().tolist())
        selected_states = st.multiselect("Select States to Compare:", options=all_states, default=all_states[:3])
        
        if selected_states:
            trend_data = data[data["Consignee State"].isin(selected_states)]
            # To order the months correctly, add Month_Order
            trend_data["Month_Order"] = trend_data["Month"].map(month_order)
            # Group by state and period
            trends_df = trend_data.groupby(["Consignee State", "Period"])["Tons"].sum().reset_index()
            # For proper ordering, we can sort by Month_Order by merging with a lookup table if needed.
            # Here, we assume the period strings order roughly chronologically.
            fig_trends = px.line(
                trends_df,
                x="Period",
                y="Tons",
                color="Consignee State",
                title="Monthly Trends for Selected States",
                markers=True
            )
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.info("Please select at least one state to display trends.")

    # ------------------------------------------------------
    # Tab 3: Growth Analysis – Period-over-Period Change
    # ------------------------------------------------------
    with tab_growth:
        st.subheader("State-Level Growth Analysis")
        # Use the Period column created above; if not present, create it.
        if "Period" not in data.columns:
            data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
        # Group by state and period
        period_state = data.groupby(["Consignee State", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(period_state)

        # Compute percentage change along the period axis
        pct_change = period_state.pct_change(axis=1) * 100
        pct_change = pct_change.round(2)
        st.markdown("#### Period-over-Period Percentage Change (%)")
        st.dataframe(pct_change)
    
    st.success("✅ State-Level Market Insights Dashboard Loaded Successfully!")
