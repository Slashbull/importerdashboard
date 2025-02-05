import streamlit as st
import pandas as pd
import gspread
from google.auth.transport.requests import Request
from google.auth import default

# Function to load Google Sheets data
def load_google_sheet(sheet_url):
    # Authenticate using the default credentials
    creds, _ = default()
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    client = gspread.authorize(creds)
    
    # Open the Google Sheet by URL and load the first sheet
    sheet = client.open_by_url(sheet_url).sheet1
    data = pd.DataFrame(sheet.get_all_records())
    return data

# Function to load data from Excel or CSV
def load_file(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file)

# Streamlit UI
st.title("Powerful Dashboard for Data Analysis")

# Sidebar for file upload or Google Sheets link
st.sidebar.title("Upload Options")

# Option 1: Google Sheets Link
sheet_url = st.sidebar.text_input("Enter Google Sheets URL")

# Option 2: Upload File (CSV or Excel)
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if sheet_url:
    data = load_google_sheet(sheet_url)
    st.write("Data loaded from Google Sheets")
elif uploaded_file is not None:
    data = load_file(uploaded_file)
    st.write(f"Data loaded from {uploaded_file.name}")
else:
    st.warning("Please upload a file or provide a Google Sheets URL.")

# Display the data
if 'data' in locals():
    st.write(data)

    # Sidebar Filters
    st.sidebar.title("Filters")
    state_filter = st.sidebar.multiselect("Select State", options=data['State'].unique(), default=data['State'].unique())
    year_filter = st.sidebar.multiselect("Select Year", options=data['Year'].unique(), default=data['Year'].unique())
    month_filter = st.sidebar.multiselect("Select Month", options=data['Month'].unique(), default=data['Month'].unique())
    consignee_filter = st.sidebar.multiselect("Select Consignee", options=data['Consignee'].unique(), default=data['Consignee'].unique())
    exporter_filter = st.sidebar.multiselect("Select Exporter", options=data['Exporter'].unique(), default=data['Exporter'].unique())

    # Filter the data
    filtered_data = data[
        data['State'].isin(state_filter) &
        data['Year'].isin(year_filter) &
        data['Month'].isin(month_filter) &
        data['Consignee'].isin(consignee_filter) &
        data['Exporter'].isin(exporter_filter)
    ]

    # Display filtered data
    st.write(filtered_data)

    # Example chart: Quantity by State
    st.subheader("Quantity by State")
    state_quantity = filtered_data.groupby('State')['Quanity'].sum().reset_index()
    st.bar_chart(state_quantity.set_index('State')['Quanity'])
