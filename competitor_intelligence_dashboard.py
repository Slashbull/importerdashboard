import streamlit as st
import pandas as pd
import plotly.express as px

def competitor_intelligence_dashboard(data: pd.DataFrame):
    st.title("🤝 Competitor Intelligence Dashboard")
    
    # Check that the required data exists
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Consignee", "Exporter", "Tons", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Ensure that the 'Tons' column is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Create tabs for different sections of the dashboard
    tab1, tab2, tab3 = st.tabs(["Top Competitors", "Exporters Used", "Growth Analysis"])

    # ---------------------------
    # Tab 1: Top Competitors by Import Volume
    # ---------------------------
    with tab1:
        st.subheader("Top Competitors by Import Volume")
        # Allow user to choose how many top competitors to display
        top_n = st.selectbox("Select number of top competitors to display:", options=[5, 10, 15], index=0)
        top_competitors = (
            data.groupby("Consignee")["Tons"]
            .sum()
            .nlargest(top_n)
            .reset_index()
        )
        fig1 = px.bar(
            top_competitors,
            x="Consignee",
            y="Tons",
            title=f"Top {top_n} Competitors by Tons",
            labels={"Tons": "Total Tons"},
            text_auto=True
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------
    # Tab 2: Exporters Used by Top Competitors
    # ---------------------------
    with tab2:
        st.subheader("Exporters Used by Top Competitors")
        # Use top 5 competitors from the previous calculation
        top_list = (
            data.groupby("Consignee")["Tons"]
            .sum()
            .nlargest(5)
            .reset_index()["Consignee"]
            .tolist()
        )
        filtered = data[data["Consignee"].isin(top_list)]
        competitor_exporters = (
            filtered.groupby(["Consignee", "Exporter"])["Tons"]
            .sum()
            .reset_index()
        )
        st.dataframe(competitor_exporters)

    # ---------------------------
    # Tab 3: Competitor Growth Over Time
    # ---------------------------
    with tab3:
        st.subheader("Competitor Growth Over Time")
        # Create a "Period" column by concatenating Month and Year
        data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
        # Group by Consignee and Period, then unstack to get a time series table per competitor
        growth = data.groupby(["Consignee", "Period"])["Tons"].sum().unstack(fill_value=0)
        st.line_chart(growth)

    st.success("✅ Competitor Intelligence Dashboard Loaded Successfully!")
