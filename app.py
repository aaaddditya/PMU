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
        "background-color": "rgb(123, 209, 146)",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "rgb(49, 51, 63)",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
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

    # New - Issues dropdown with multiple selection
    issues_options = ['Disputes', 'Leader Activation', 'Joinings', 'Alliance Coordination', 'Organizational Issue']
    selected_issues = st.multiselect('Issues', options=issues_options)

    # Issues Details (text input for each selected issue)
    issues_details = {}
    for issue in selected_issues:
        issues_details[issue] = st.text_area(f"Issues Details for {issue}")

    # Narrative
    narrative = st.text_area('Narrative')

    # Escalation Detail (text input)
    escalation_detail = st.text_area('Escalation Detail')

    # Escalation levels (dropdown with custom options)
    escalation_level = st.selectbox('Escalation Levels', options=['Alert', 'Mid Alert', 'Normal'])
    Issue_raised = st.selectbox('Issue Raised to', options=['Anurag', 'Anant', 'Alimpan Banerjee'])

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
                'Issues': selected_issues[i] if i < len(selected_issues) else '',
                'Issues Details': issues_details.get(selected_issues[i], '') if i < len(selected_issues) else '',
                'Narrative': narrative,
                'Escalation Detail': escalation_detail,
                'Escalation Level': escalation_level,
                'Issue Raised to': Issue_raised
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
        # Show Zone at the top
        st.subheader(f"Zone: {ac_details['Zone']}")
        
        # Create two columns for District (left) and AC Name + AC No (right)
        col1, col2 ,col3= st.columns(3)
        with col1:
            st.text(f"District: {ac_details['District']}")
        with col2:
            st.text(f"AC Name: {ac_details['AC Name']}")
        with col3:    
            st.text(f"AC No: {ac_details['AC No']}")
        
        # Create a row with Current MLA, Party, Margin_2019, GE2024 Status, Margin_2024
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(f"Current MLA: {ac_details['Current MLA']}")
        with col2:
            st.text(f"Party: {ac_details['Party']}")
        with col3:
            st.text(f"Margin 2019: {ac_details['Margin_2019']}")
        with col4:
            st.text(f"GE2024 Status: {ac_details['GE2024 Status']}")
        with col5:
            st.text(f"Margin 2024: {ac_details['Margin_2024']}")

        st.write("---")

        # Fetch data from DDMMYYYY.csv
        ddmm_data = load_ddmm_data(selected_date, selected_ac_name)
        if ddmm_data is not None and not ddmm_data.empty:
            for index, row in ddmm_data.iterrows():
                # Display Date and Issue Raised To
                col1, col2 = st.columns(2)
                with col1:
                    st.text(f"Date: {row['Date']}")
                with col2:
                    st.text(f"Issue Raised To: {row['Issue Raised to']}")

                # Display Escalation Level and Escalation Detail
                col1, col2 = st.columns(2)
                with col1:
                    st.text(f"Escalation Level: {row['Escalation Level']}")
                with col2:
                    st.text(f"Escalation Detail: {row['Escalation Detail']}")

                # Display Narrative in the middle
                st.text(f"Narrative: {row['Narrative']}")
                st.write("---")
                break
            for index, row in ddmm_data.iterrows():
                # Display Date and Issue Raised To
        
                # Display Alliance Party and Alliance Activity
                col1, col2 = st.columns(2)
                with col1:
                    if type(row['Alliance Party'])==str: 
                
                        st.text(f"Alliance Party: {row['Alliance Party']}")
                with col2:
                    if type(row['Alliance Activity'])==str:

                        st.text(f"Alliance Activity: {row['Alliance Activity']}")

                # Display Opposition Party and Opposition Activity
                col1, col2 = st.columns(2)
                with col1:
                    if type(row['Opposition Party'])==str:
                        st.text(f"Opposition Party: {row['Opposition Party']}")
                with col2:
                    if type(row['Opposition Activity'])==str:
                        st.text(f"Opposition Activity: {row['Opposition Activity']}")

                # Display Issues and Issues Details
                col1, col2 = st.columns(2)
                with col1:
                    if type(row['Issues'])==str:
                        st.text(f"Issues: {row['Issues']}")
                with col2:
                    if type(row['Issues Details'])==str:
                        st.markdown(f"<p style='font-family:sans-serif; color:Green; font-size: 42px;'>Issues Details: {row['Issues Details']}</p>", unsafe_allow_html=True)
        else:
            st.warning(f"No data available for the selected date and AC Name.")

    else:
        st.error(f"No data found for AC Name: {selected_ac_name}")

# Home Page Functionality
def home_page():
    st.title("Home")
    st.write("Welcome to the MLA Activities Dashboard! Use the navigation to input data or view the dashboard.")
    new_title = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">Aditya</p>'
    st.markdown(new_title, unsafe_allow_html=True)
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
