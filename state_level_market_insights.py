import streamlit as st
import pandas as pd
import plotly.express as px

def state_level_market_insights(data: pd.DataFrame):
    st.title("🌍 State-Level Market Insights Dashboard")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee State", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    
    tab_overview, tab_trends, tab_growth, tab_details = st.tabs(["Overview", "Trends", "Growth Analysis", "Detailed Analysis"])
    
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
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Top Importing States")
        top_states = state_agg.sort_values("Tons", ascending=False).head(5)
        fig_bar = px.bar(top_states, x="Consignee State", y="Tons",
                         title="Top 5 States by Tons", labels={"Tons": "Total Tons"},
                         text_auto=True, color="Tons")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab_trends:
        st.subheader("Overall Monthly Trends by State")
        trends_df = data.groupby(["Consignee State", "Period"])["Tons"].sum().reset_index()
        fig_trends = px.line(trends_df, x="Period", y="Tons", color="Consignee State",
                             title="Monthly Trends by State", markers=True)
        st.plotly_chart(fig_trends, use_container_width=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Detailed Trends for Selected States")
        all_states = sorted(data["Consignee State"].dropna().unique().tolist())
        selected_states = st.multiselect("Select States", options=all_states, default=all_states[:3])
        if selected_states:
            detailed_trends = data[data["Consignee State"].isin(selected_states)]
            detailed_df = detailed_trends.groupby(["Consignee State", "Period"])["Tons"].sum().reset_index()
            fig_detail = px.line(detailed_df, x="Period", y="Tons", color="Consignee State",
                                 title="Detailed Trends for Selected States", markers=True)
            st.plotly_chart(fig_detail, use_container_width=True)
        else:
            st.info("Please select at least one state for detailed analysis.")
    
    with tab_growth:
        st.subheader("Growth Analysis by State (Slope Chart)")
        pivot_table = data.pivot_table(index="Consignee State", columns="Period", values="Tons",
                                        aggfunc="sum", fill_value=0)
        periods = sorted(pivot_table.columns)
        if len(periods) < 2:
            st.info("Not enough periods available for growth analysis.")
        else:
            first_period = periods[0]
            last_period = periods[-1]
            growth_df = pivot_table[[first_period, last_period]].reset_index()
            growth_df["Growth (%)"] = ((growth_df[last_period] - growth_df[first_period]) / 
                                       growth_df[first_period].replace(0, pd.NA)) * 100
            growth_df["Growth (%)"] = growth_df["Growth (%)"].round(2)
            st.markdown(f"#### Growth from {first_period} to {last_period}")
            import plotly.graph_objects as go
            fig_slope = go.Figure()
            for idx, row in growth_df.iterrows():
                fig_slope.add_trace(go.Scatter(
                    x=[row[first_period], row[last_period]],
                    y=[row["Consignee State"], row["Consignee State"]],
                    mode="lines+markers",
                    marker=dict(size=10),
                    line=dict(width=2),
                    name=row["Consignee State"],
                    hovertemplate=(
                        f"State: {row['Consignee State']}<br>" +
                        f"{first_period}: {row[first_period]:,.2f} Tons<br>" +
                        f"{last_period}: {row[last_period]:,.2f} Tons<br>" +
                        f"Growth: {row['Growth (%)'] if pd.notna(row['Growth (%)']) else 'N/A'}%"
                    )
                ))
            fig_slope.update_layout(title=f"State Growth from {first_period} to {last_period}",
                                      xaxis_title="Volume (Tons)",
                                      yaxis_title="Consignee State",
                                      showlegend=False)
            st.plotly_chart(fig_slope, use_container_width=True)
            st.markdown("#### Detailed Growth Data")
            st.dataframe(growth_df[["Consignee State", first_period, last_period, "Growth (%)"]])
    
    with tab_details:
        st.subheader("Detailed State-Level Data")
        detailed_pivot = data.pivot_table(index="Consignee State", columns="Period", values="Tons",
                                          aggfunc="sum", fill_value=0)
        st.dataframe(detailed_pivot)
        st.markdown("#### Summary Table by State")
        summary_table = data.groupby("Consignee State")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        st.dataframe(summary_table)
    
    st.success("✅ State-Level Market Insights Dashboard Loaded Successfully!")
