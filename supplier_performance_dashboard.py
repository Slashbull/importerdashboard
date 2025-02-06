import streamlit as st
import pandas as pd

# ---- Supplier Performance Dashboard ---- #
def supplier_performance_dashboard():
    st.title("📊 Supplier Performance Dashboard")

    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    df = st.session_state["uploaded_data"]

    # Ensure required columns exist
    required_columns = ["Exporter", "Kgs"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"🚨 Missing columns in the dataset: {', '.join(missing_columns)}")
        return

    # Convert Kgs to numeric if not already
    df["Kgs"] = pd.to_numeric(df["Kgs"], errors="coerce")

    st.markdown("### 🏆 Top Suppliers by Volume")
    top_suppliers = df.groupby("Exporter")["Kgs"].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_suppliers)

    st.markdown("### 📈 Supplier Consistency Analysis")
    if "Month" in df.columns and "Year" in df.columns:
        df["Period"] = df["Month"] + "-" + df["Year"].astype(str)
        supplier_trends = df.groupby(["Exporter", "Period"])["Kgs"].sum().unstack(fill_value=0)
        st.line_chart(supplier_trends)
    else:
        st.warning("⚠️ Columns 'Month' and 'Year' are required for consistency analysis.")

    st.markdown("### 🚨 Flagging Risky Suppliers")
    supplier_stats = df.groupby("Exporter")["Kgs"].agg(["sum", "mean", "std"])
    risky_suppliers = supplier_stats[supplier_stats["std"] > (supplier_stats["mean"] * 0.5)]  # Example risk metric
    st.write("#### Risky Suppliers:")
    st.dataframe(risky_suppliers)

    st.success("✅ Supplier Performance Dashboard Loaded Successfully!")
