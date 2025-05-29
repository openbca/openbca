import streamlit as st
import pandas as pd

st.set_page_config(page_title="Multi-Tab Table Editor with Metrics", layout="centered")

st.title("📁 Multi-Tab Table Editor with Metrics")

# Sample initial data for each tab
data_sources = {
    "Fruits": pd.DataFrame({
        "Item": ["Apple", "Banana", "Cherry"],
        "Quantity": [10, 15, 7],
        "Price": [0.5, 0.3, 1.0],
    }),
    "Vegetables": pd.DataFrame({
        "Item": ["Tomato", "Carrot", "Lettuce"],
        "Quantity": [20, 12, 8],
        "Price": [0.4, 0.25, 0.6],
    }),
    "Dairy": pd.DataFrame({
        "Item": ["Milk", "Cheese", "Yogurt"],
        "Quantity": [5, 3, 10],
        "Price": [1.2, 2.5, 0.9],
    }),
    "Sales Over Time": pd.DataFrame({
        "Date": pd.date_range("2024-01-01", periods=7, freq='D'),
        "Sales": [100, 120, 130, 90, 150, 170, 160],
        "Price": [1.2, 1.3, 1.25, 1.1, 1.5, 1.55, 1.6]
    })
}

# Dictionary to store edited tables
edited_tables = {}

# Tabs for each category
tabs = st.tabs(list(data_sources.keys()))

# Display each table in its respective tab
for tab_name, tab, initial_df in zip(data_sources.keys(), tabs, data_sources.values()):
    with tab:
        st.subheader(f"{tab_name} Table")
        edited_df = st.data_editor(initial_df, num_rows="dynamic", use_container_width=True)

        # Store the edited table
        edited_tables[tab_name] = edited_df

        # Special case: Time series chart
        if tab_name == "Sales Over Time":
            st.markdown("**📉 Sales Trend Over Time:**")
            try:
                edited_df["Date"] = pd.to_datetime(edited_df["Date"])
                chart_df = edited_df.sort_values("Date")
                st.line_chart(chart_df.set_index("Date")[["Sales"]])
            except Exception as e:
                st.warning(f"⚠️ Could not render chart: {e}")
        else:
            # Per-tab metrics
            st.markdown("**📊 Metrics for This Table:**")
            try:
                edited_df["Total"] = edited_df["Quantity"] * edited_df["Price"]
                total_items = edited_df["Quantity"].sum()
                total_cost = edited_df["Total"].sum()
                avg_price = edited_df["Price"].mean()

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Quantity", int(total_items))
                col2.metric("Total Value ($)", f"{total_cost:.2f}")
                col3.metric("Average Price ($)", f"{avg_price:.2f}")
            except Exception as e:
                st.warning(f"Could not calculate metrics: {e}")

# ---- Global Metrics Across All Tabs ----
st.divider()
st.subheader("🌐 Global Metrics Across All Tables")

try:
    # Concatenate all non-time series tables
    all_data = pd.concat([
        df for name, df in edited_tables.items()
        if name != "Sales Over Time"
    ], ignore_index=True)

    all_data["Total"] = all_data["Quantity"] * all_data["Price"]

    total_items_all = all_data["Quantity"].sum()
    total_value_all = all_data["Total"].sum()
    avg_price_all = all_data["Price"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quantity (All)", int(total_items_all))
    col2.metric("Total Value (All)", f"{total_value_all:.2f}")
    col3.metric("Avg Price (All)", f"{avg_price_all:.2f}")
except Exception as e:
    st.error(f"⚠️ Failed to compute global metrics: {e}")
