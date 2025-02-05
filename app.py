import streamlit as st
import pandas as pd

# Load the data
@st.cache
def load_data():
    data = pd.read_csv('path_to_your_uploaded_data/Data.csv')
    return data

# Load the data
data = load_data()

# Display the dataset on the app
st.title("Powerful Dashboard for Data Analysis")
st.write("This is your powerful dashboard!")

# Dynamic Filters
st.sidebar.title("Filters")
state_filter = st.sidebar.multiselect("Select State", options=data['State'].unique(), default=data['State'].unique())
year_filter = st.sidebar.multiselect("Select Year", options=data['Year'].unique(), default=data['Year'].unique())
month_filter = st.sidebar.multiselect("Select Month", options=data['Month'].unique(), default=data['Month'].unique())
consignee_filter = st.sidebar.multiselect("Select Consignee", options=data['Consignee'].unique(), default=data['Consignee'].unique())
exporter_filter = st.sidebar.multiselect("Select Exporter", options=data['Exporter'].unique(), default=data['Exporter'].unique())

# Filter the data based on user input
filtered_data = data[
    data['State'].isin(state_filter) &
    data['Year'].isin(year_filter) &
    data['Month'].isin(month_filter) &
    data['Consignee'].isin(consignee_filter) &
    data['Exporter'].isin(exporter_filter)
]

# Display the filtered data in the dashboard
st.write(filtered_data)

# Example chart: Quantity distribution by State
st.subheader("Quantity by State")
state_quantity = filtered_data.groupby('State')['Quanity'].sum().reset_index()
st.bar_chart(state_quantity.set_index('State')['Quanity'])
