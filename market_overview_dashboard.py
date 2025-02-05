import streamlit as st
import polars as pl
import matplotlib.pyplot as plt
from io import StringIO

# ---- Market Overview Dashboard ---- #
def market_dashboard(uploaded_data):
    st.title("📊 Market Overview Dashboard")
    st.markdown("""
    Gain insights into total imports, top states, suppliers, and trends.
    Use filters to refine your analysis and explore market behavior.
    """)

    # ---- Process Uploaded Data ---- #
    @st.cache_data(max_entries=10)
    def load_data(data):
        df = pl.read_csv(StringIO(data.decode("utf-8")))
        df = df.with_columns([
            pl.col("Quanity (Kgs)").str.replace(" Kgs", "").cast(pl.Float64),
            pl.col("Quanity (Tons)").str.replace(" tons", "").cast(pl.Float64)
        ])
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                     "Jul": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        if "Month" in df.columns:
            df = df.with_columns(pl.col("Month").replace(month_map))
        else:
            st.error("🚨 Error: 'Month' column is missing in uploaded data.")
            return None
        return df

    df = load_data(uploaded_data)
    if df is None:
        return

    # ---- Filters ---- #
    st.sidebar.header("Filters")
    selected_state = st.sidebar.selectbox("Select State", options=["All"] + df["Consignee State"].unique().to_list())
    selected_consignee = st.sidebar.selectbox("Select Consignee", options=["All"] + df["Consignee"].unique().to_list())
    selected_exporter = st.sidebar.selectbox("Select Exporter", options=["All"] + df["Exporter"].unique().to_list())
    selected_month = st.sidebar.selectbox("Select Month", options=["All"] + df["Month"].unique().to_list())
    selected_year = st.sidebar.selectbox("Select Year", options=["All"] + df["Year"].unique().to_list())
    selected_product = st.sidebar.selectbox("Select Product", options=["All"] + df["Mark"].unique().to_list())
    quantity_toggle = st.sidebar.radio("View Data As", ("Quantity (Kgs)", "Quantity (Tons)"))

    # Apply Filters
    filtered_data = df
    if selected_state != "All":
        filtered_data = filtered_data.filter(pl.col("Consignee State") == selected_state)
    if selected_consignee != "All":
        filtered_data = filtered_data.filter(pl.col("Consignee") == selected_consignee)
    if selected_exporter != "All":
        filtered_data = filtered_data.filter(pl.col("Exporter") == selected_exporter)
    if selected_month != "All":
        filtered_data = filtered_data.filter(pl.col("Month") == selected_month)
    if selected_year != "All":
        filtered_data = filtered_data.filter(pl.col("Year") == int(selected_year))
    if selected_product != "All":
        filtered_data = filtered_data.filter(pl.col("Mark") == selected_product)

    # Set Quantity Column
    quantity_col = "Quanity (Kgs)" if quantity_toggle == "Quantity (Kgs)" else "Quanity (Tons)"

    # ---- Key Metrics ---- #
    st.subheader("Key Metrics")
    col1, col2 = st.columns(2)
    col1.metric(f"Total Import Volume ({quantity_toggle})", f"{filtered_data[quantity_col].sum():,.2f}")
    col2.metric("Unique Exporters", len(filtered_data["Exporter"].unique()))

    # ---- Visualizations ---- #
    st.subheader("Visualizations")

    # Monthly Import Trends
    st.write("### Monthly Import Trends")
    monthly_trends = filtered_data.groupby("Month")[quantity_col].sum().sort("Month")
    fig, ax = plt.subplots()
    ax.plot(monthly_trends["Month"], monthly_trends[quantity_col], marker="o")
    ax.set_title("Monthly Import Trends")
    ax.set_xlabel("Month")
    ax.set_ylabel(f"Total Quantity ({quantity_toggle})")
    ax.grid(True)
    st.pyplot(fig)

    # Top 5 States by Import Volume
    st.write("### Top 5 States by Import Volume")
    top_states = filtered_data.groupby("Consignee State")[quantity_col].sum().sort(quantity_col, reverse=True).head(5)
    fig, ax = plt.subplots()
    ax.bar(top_states["Consignee State"], top_states[quantity_col])
    ax.set_title("Top 5 States by Import Volume")
    ax.set_xlabel("State")
    ax.set_ylabel(f"Total Quantity ({quantity_toggle})")
    st.pyplot(fig)

    # Top 5 Exporters by Import Volume
    st.write("### Top 5 Exporters by Import Volume")
    top_exporters = filtered_data.groupby("Exporter")[quantity_col].sum().sort(quantity_col, reverse=True).head(5)
    fig, ax = plt.subplots()
    ax.bar(top_exporters["Exporter"], top_exporters[quantity_col])
    ax.set_title("Top 5 Exporters by Import Volume")
    ax.set_xlabel("Exporter")
    ax.set_ylabel(f"Total Quantity ({quantity_toggle})")
    st.pyplot(fig)

    # ---- Download Button ---- #
    st.download_button("📥 Download Filtered Data", filtered_data.write_csv(), "filtered_data.csv", "text/csv")

# Save file as market_overview_dashboard.py
