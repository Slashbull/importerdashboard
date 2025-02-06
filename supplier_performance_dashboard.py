import streamlit as st
import pandas as pd
import plotly.express as px

def supplier_performance_dashboard(data: pd.DataFrame):
    st.title("📊 Supplier Performance Dashboard")

    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    required_columns = ["Exporter", "Kgs", "Month", "Year"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    data["Kgs"] = pd.to_numeric(data["Kgs"], errors="coerce")

    st.markdown("### 🏆 Top Suppliers by Volume")
    top_suppliers = data.groupby("Exporter")["Kgs"].sum().nlargest(5).reset_index()
    fig1 = px.bar(top_suppliers, x="Exporter", y="Kgs", title="Top Suppliers")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 📈 Supplier Consistency Analysis")
    data["Period"] = data["Month"] + "-" + data["Year"].astype(str)
    supplier_trends = data.groupby(["Exporter", "Period"])["Kgs"].sum().unstack(fill_value=0)
    st.line_chart(supplier_trends)

    st.markdown("### 🚨 Flagging Risky Suppliers")
    stats = data.groupby("Exporter")["Kgs"].agg(["sum", "mean", "std"])
    risky = stats[stats["std"] > (stats["mean"] * 0.5)]
    st.dataframe(risky)
    
    st.success("✅ Supplier Performance Dashboard Loaded Successfully!")
