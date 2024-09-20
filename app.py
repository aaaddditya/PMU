import streamlit as st
import pandas as pd
import os
from datetime import date

# Function to load the data for the dashboard (based on the selected date and AC name)
def load_data(selected_date, selected_ac_name):
    file_name = f"{selected_date.strftime('%d%m%Y')}.csv"
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        # Filter the data by AC Name
        filtered_df = df[df['AC Name'] == selected_ac_name]
        return filtered_df
    else:
        return None

# Navbar Functionality (Tab navigation)
def display_navbar():
    # Define the tabs
    tabs = ["Home", "Input", "Dashboard"]
    tab = st.sidebar.radio("Navigation", tabs)
    return tab

# Input Form Functionality
def input_form(df):
    st.title("Input Data for MLA Activities")

    # Date (default value is today)
    input_date = st.date_input('Date', value=date.today())

    # AC Name dropdown (from 3rd column of loaded data)
    unique_ac_names = df.iloc[:, 2].unique()
    ac_name = st.selectbox('AC Name', options=unique_ac_names)

    # Name of person
    person_name = st.text_input('Name of Person')

    # Alliance Party name (multi-select)
    unique_party_names = df.iloc[:, 5].unique()
    alliance_parties = st.multiselect('Alliance Party Name', options=unique_party_names)

    # Alliance Party Activity details (one text box per selected Alliance party)
    alliance_activity_details = {}
    for party in alliance_parties:
        alliance_activity_details[party] = st.text_area(f"Activity Details for {party}")

    # Opposition Party name (multi-select)
    opposition_parties = st.multiselect('Opposition Party Name', options=unique_party_names)

    # Opposition Party Activity details (one text box per selected Opposition party)
    opposition_activity_details = {}
    for party in opposition_parties:
        opposition_activity_details[party] = st.text_area(f"Opposition Details for {party}")

    # Narrative
    narrative = st.text_area('Narrative')

    # Escalation Detail (text input)
    escalation_detail = st.text_area('Escalation Detail')

    # Escalation levels (dropdown with custom options)
    escalation_level = st.selectbox('Escalation Levels', options=['Alert', 'Mid Alert', 'Normal'])

    # Button to submit the data
    if st.button('Submit'):
        # Find the max number of rows (max number of Alliance and Opposition parties)
        max_rows = max(len(alliance_parties), len(opposition_parties))

        # Prepare the data for the CSV
        rows = []
        for i in range(max_rows):
            row = {
                'Date': input_date,
                'AC Name': ac_name,
                'Person Name': person_name,
                'Alliance Party': alliance_parties[i] if i < len(alliance_parties) else '',
                'Alliance Activity': alliance_activity_details.get(alliance_parties[i], '') if i < len(alliance_parties) else '',
                'Opposition Party': opposition_parties[i] if i < len(opposition_parties) else '',
                'Opposition Activity': opposition_activity_details.get(opposition_parties[i], '') if i < len(opposition_parties) else '',
                'Narrative': narrative,
                'Escalation Detail': escalation_detail,
                'Escalation Level': escalation_level
            }
            rows.append(row)

        # Convert rows into DataFrame
        df_new = pd.DataFrame(rows)

        # Define today's date in DDMMYYYY format and prepare file name
        today_str = date.today().strftime("%d%m%Y")
        file_name = f"{today_str}.csv"

        # Check if the CSV file for today already exists, and if so, append data
        if os.path.exists(file_name):
            df_existing = pd.read_csv(file_name)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(file_name, index=False)
        else:
            df_new.to_csv(file_name, index=False)

        st.success(f"Data successfully saved to {file_name}")

# Dashboard Functionality
def dashboard():
    st.title("Dashboard")

    # Date input for filtering the CSV
    selected_date = st.date_input('Select Date for Data', value=date.today())

    # Load unique AC Names from a sample CSV (for dropdown)
    df_sample = pd.read_csv('288_MLA.csv')
    unique_ac_names = df_sample.iloc[:, 2].unique()
    selected_ac_name = st.selectbox('Select AC Name', options=unique_ac_names)

    # Submit button to display filtered data
    if st.button('Show Data'):
        filtered_data = load_data(selected_date, selected_ac_name)
        if filtered_data is not None and not filtered_data.empty:
            st.write(filtered_data)
        else:
            st.warning("No data available for the selected date and AC Name.")

# Home Page Functionality
def home_page():
    st.title("Home")
    st.write("Welcome to the MLA Activities Dashboard! Use the navigation to input data or view the dashboard.")

# Main Streamlit App
def main():
    # Display the navigation bar and switch between tabs
    tab = display_navbar()

    # Load data for input form
    df = pd.read_csv('288_MLA.csv')

    # Home tab
    if tab == "Home":
        home_page()

    # Input tab
    elif tab == "Input":
        input_form(df)

    # Dashboard tab
    elif tab == "Dashboard":
        dashboard()

if __name__ == "__main__":
    main()
