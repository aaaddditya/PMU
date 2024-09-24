import streamlit as st
import pandas as pd
import os
from datetime import date
import numpy as np
from streamlit_navigation_bar import st_navbar

st.set_page_config(
    layout="wide",
)


def load_data(selected_date, selected_ac_name):
    file_name = f"{selected_date.strftime('%d%m%Y')}.csv"
    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name)
            if df.empty:
                st.warning("The file is empty. No data available.")
                return None
            # Filter the data by AC Name
            filtered_df = df[df['AC Name'] == selected_ac_name]
            return filtered_df
        except pd.errors.EmptyDataError:
            st.error(f"The file {file_name} is empty.")
            return None
    else:
        st.warning(f"No data file found for the date {selected_date.strftime('%d%m%Y')}.")
        return None

# Function to load AC data from 118_AC_list.csv
def load_ac_data(ac_name):
    ac_data = pd.read_csv('118_AC_list.csv')
    # Filter the data for the selected AC Name
    filtered_ac_data = ac_data[ac_data['AC Name'] == ac_name]
    if not filtered_ac_data.empty:
        return filtered_ac_data.iloc[0]  # Return the first matching row
    else:
        return None
    
def load_ddmm_data(selected_date, ac_name):
    file_name = f"{selected_date.strftime('%d%m%Y')}.csv"
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        # Filter the data by AC Name
        filtered_df = df[df['AC Name'] == ac_name]
        return filtered_df
    else:
        return None
        
# Navbar Functionality (Tab navigation)
def display_navbar():
    # Define the tabs
    tabs = ["Home", "Input", "Dashboard"]
    styles = {
    "nav": {
        "background-color": "rgb(17, 45, 78)",
        "color": "rgb(255,255,255)"
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "rgb(255,255,255)",
        "font-weight": "700",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
        "color": "rgb(255,255,255)"
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
}
    # tab = st.sidebar.radio("Navigation", tabs)
    tab=st_navbar(["Home", "Input", "Dashboard"], styles=styles)
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

    # Renamed Issues to Escalation dropdown with multiple selection
    escalation_options = ['Disputes', 'Leader Activation', 'Joinings', 'Alliance Coordination', 'Organizational Issue']
    selected_escalations = st.multiselect('Escalation', options=escalation_options)

    # For each Escalation, we ask for Escalation Detail, Escalation Level, and Issue Raised To
    escalation_details = []
    for escalation in selected_escalations:
        st.markdown(f"### Escalation Details for {escalation}")
        
        # Escalation Detail text input
        detail = st.text_area(f"Escalation Detail for {escalation}")
        
        # Escalation Level
        level = st.selectbox(f'Escalation Level for {escalation}', options=['Alert', 'Mid Alert', 'Normal'])
        
        # Issue Raised To
        raised_to = st.selectbox(f'Issue Raised to for {escalation}', options=['Anurag', 'Anant', 'Alimpan Banerjee'])
        
        # Store all details in a dictionary for this escalation
        escalation_details.append({
            'Escalation': escalation,
            'Escalation Detail': detail,
            'Escalation Level': level,
            'Issue Raised To': raised_to
        })

    # Narrative
    narrative = st.text_area('Narrative')

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
                'Narrative': narrative
            }
            rows.append(row)

        # Add Escalation details to rows
        for escalation_detail in escalation_details:
            row = {
                'Date': input_date,
                'AC Name': ac_name,
                'Person Name': person_name,
                'Escalation': escalation_detail['Escalation'],
                'Escalation Detail': escalation_detail['Escalation Detail'],
                'Escalation Level': escalation_detail['Escalation Level'],
                'Issue Raised To': escalation_detail['Issue Raised To'],
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

def display_dashboard():
    st.title("AC Dashboard")

    # Date and AC Name input
    selected_date = st.date_input('Select Date for Data', value=date.today())

    # Load unique AC Names from 118_AC_list.csv
    ac_list = pd.read_csv('118_AC_list.csv')
    unique_ac_names = np.sort(ac_list['AC Name'].unique())
    selected_ac_name = st.selectbox('Select AC Name', options=unique_ac_names)

    # Fetch and display AC details from 118_AC_list.csv
    ac_details = load_ac_data(selected_ac_name)
    if ac_details is not None:
        st.subheader(f"Zone: {ac_details['Zone']}")

        col1, col2 ,col3 = st.columns(3)
        col1.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:700;">District: {ac_details["District"]}</p>', unsafe_allow_html=True)
        col2.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:bold;">AC Name: {ac_details["AC Name"]}</p>', unsafe_allow_html=True)
        col3.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:bold;">AC No: {ac_details["AC No"]}</p>', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:bold;">Current MLA: {ac_details["Current MLA"]}</p>', unsafe_allow_html=True)
        col2.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:bold;">Party: {ac_details["Party"]}</p>', unsafe_allow_html=True)
        col3.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:bold;">Margin 2019: {ac_details["Margin_2019"]}</p>', unsafe_allow_html=True)
        col4.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:bold;">GE2024 Status: {ac_details["GE2024 Status"]}</p>', unsafe_allow_html=True)
        col5.markdown(f'<p style="font-family:sans-serif;font-size:20px;font-weight:bold;">Margin 2024: {ac_details["Margin_2024"]}</p>', unsafe_allow_html=True)

        st.write("---")

        # Fetch data from DDMMYYYY.csv
        ddmm_data = load_ddmm_data(selected_date, selected_ac_name)
        if ddmm_data is not None and not ddmm_data.empty:
            # Iterate over the rows in the CSV data
            for index, row in ddmm_data.iterrows():
                # Display Date
                if type(row['Escalation'])==str:
                    if row['Escalation Update']!='Resolved':
                        st.markdown(f"**Date:** {row['Date']}")

                        # Display Escalation details in a well-structured format
                        st.markdown(f"""
                        <div style="border: 1px solid #e0e0e0; padding: 10px; border-radius: 5px;">
                            <p><strong>Escalation:</strong> {row['Escalation']}</p>
                            <p><strong>Escalation Detail:</strong> {row['Escalation Detail']}</p>
                            <p><strong>Escalation Level:</strong> {row['Escalation Level']}</p>
                            <p><strong>Issue Raised To:</strong> {row['Issue Raised To']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Provide a dropdown for updating the Escalation status
                        escalation_update = st.selectbox(
                            f"Escalation Update for {row['Escalation']}", 
                            options=['Pending', 'Resolved'],
                            key=f"update_{index}"
                        )

                        # Add a submit button to update the status in the CSV
                        if st.button(f'Update Status for {row["Escalation"]}', key=f'button_{index}'):
                            # Add Escalation Update to the dataframe
                            ddmm_data.at[index, 'Escalation Update'] = escalation_update

                            # Save the updated data back to the CSV
                            today_str = selected_date.strftime("%d%m%Y")
                            file_name = f"{today_str}.csv"
                            ddmm_data.to_csv(file_name, index=False)

                            st.success(f"Escalation status for {row['Escalation']} updated to {escalation_update} in {file_name}")

                        st.write("---")
        else:
            st.warning(f"No data available for the selected date and AC Name.")
    
    else:
        st.error(f"No data found for AC Name: {selected_ac_name}")

    
# Home Page Functionality
def home_page():
    st.title("Home")
    st.write("Welcome to the MLA Activities Dashboard! Use the navigation to input data or view the dashboard.")
    # new_title = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">Aditya</p>'
    # st.markdown(new_title, unsafe_allow_html=True)
# Main Streamlit App
def main():
    # Display the navigation bar and switch between tabs
    # page = st_navbar(["Home", "Input", "Dashboard"])
    tab = display_navbar()

    # Load data for input formstreamlit 
    df = pd.read_csv('288_MLA.csv')

    # Home tab
    if tab == "Home":
        home_page()

    # Input tab
    elif tab == "Input":
        input_form(df)

    # Dashboard tab
    elif tab == "Dashboard":
        display_dashboard()

if __name__ == "__main__":
    main()
