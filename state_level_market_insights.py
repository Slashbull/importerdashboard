import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

def state_level_market_insights(data: pd.DataFrame):
    st.title("🌍 State-Level Market Insights Dashboard")
    
    # --- Data Validation ---
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee State", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert "Tons" to numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create "Period" field if not already present.
    if "Period" not in data.columns:
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    
    # Predefined month ordering (if needed for sorting).
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    # --- Tab Layout ---
    # Four main tabs: Overview, Trends, Detailed Analysis, and Geospatial.
    tab_overview, tab_trends, tab_detailed, tab_geo = st.tabs([
        "Overview", "Trends", "Detailed Analysis", "Geospatial"
    ])
    
    # ----- Tab 1: Overview -----
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
    
    # ----- Tab 2: Trends -----
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
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Detailed Trends for Selected States")
        all_states = sorted(data["Consignee State"].dropna().unique().tolist())
        selected_states = st.multiselect("Select States", options=all_states, default=all_states[:3], key="state_trends")
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
    
    # ----- Tab 3: Detailed Analysis -----
    with tab_detailed:
        st.subheader("Detailed State-Level Data")
        # Pivot table by state and period.
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
        
        with st.expander("Monthly Analysis"):
            st.markdown("##### Monthly Volume and Trends")
            all_periods = sorted(data["Period"].dropna().unique().tolist())
            selected_periods = st.multiselect("Select Period(s):", options=all_periods, default=all_periods, key="state_period")
            monthly_pivot = data.pivot_table(
                index="Consignee State",
                columns="Period",
                values="Tons",
                aggfunc="sum",
                fill_value=0
            )
            if selected_periods:
                monthly_pivot = monthly_pivot[[col for col in monthly_pivot.columns if col in selected_periods]]
            monthly_pivot["Total"] = monthly_pivot.sum(axis=1)
            monthly_total_row = pd.DataFrame(monthly_pivot.sum(axis=0)).T
            monthly_total_row.index = ["Total"]
            monthly_pivot_with_total = pd.concat([monthly_pivot, monthly_total_row])
            st.dataframe(monthly_pivot_with_total)
            monthly_trends = data.groupby(["Consignee State", "Period"])["Tons"].sum().reset_index()
            fig_monthly = px.line(
                monthly_trends,
                x="Period",
                y="Tons",
                color="Consignee State",
                title="Monthly Trends Comparison",
                markers=True
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with st.expander("Yearly Analysis"):
            st.markdown("##### Yearly Volume and Trends")
            yearly_pivot = data.pivot_table(
                index="Consignee State",
                columns="Year",
                values="Tons",
                aggfunc="sum",
                fill_value=0
            )
            yearly_pivot["Total"] = yearly_pivot.sum(axis=1)
            yearly_total_row = pd.DataFrame(yearly_pivot.sum(axis=0)).T
            yearly_total_row.index = ["Total"]
            yearly_pivot_with_total = pd.concat([yearly_pivot, yearly_total_row])
            st.dataframe(yearly_pivot_with_total)
            yearly_trends = data.groupby(["Consignee State", "Year"])["Tons"].sum().reset_index()
            fig_yearly = px.line(
                yearly_trends,
                x="Year",
                y="Tons",
                color="Consignee State",
                title="Yearly Trends Comparison",
                markers=True
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
    
    # ----- Tab 4: Geospatial -----
    with tab_geo:
        st.subheader("Geospatial Analysis")
        st.markdown(
            "This map displays the total imports (in Tons) aggregated by state. "
            "Please ensure you have a valid GeoJSON file for India states with matching state names."
        )
        # Load the GeoJSON file.
        geojson_path = "india_states.geojson"  # Adjust path if needed.
        if not os.path.exists(geojson_path):
            st.error("🚨 GeoJSON file 'india_states.geojson' not found. Please ensure the file exists in the project directory.")
        else:
            try:
                with open(geojson_path, "r") as f:
                    geojson_data = json.load(f)
            except Exception as e:
                st.error("🚨 Error loading GeoJSON file.")
                st.error(e)
                return

            # Group data by state.
            state_data = data.groupby("Consignee State")["Tons"].sum().reset_index()
            # Rename the column to "state" for matching.
            state_data.rename(columns={"Consignee State": "state"}, inplace=True)
            
            # Create a choropleth map.
            fig_geo = px.choropleth_mapbox(
                state_data,
                geojson=geojson_data,
                locations="state",
                featureidkey="properties.NAME_1",  # Adjust if your GeoJSON uses a different key.
                color="Tons",
                color_continuous_scale="Viridis",
                mapbox_style="carto-positron",
                zoom=3.5,
                center={"lat": 22, "lon": 80},
                opacity=0.7,
                labels={"Tons": "Total Tons"}
            )
            fig_geo.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_geo, use_container_width=True)
    
    st.success("✅ State-Level Market Insights Dashboard Loaded Successfully!")
