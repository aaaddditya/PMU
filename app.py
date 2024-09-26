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
    tab=st_navbar(["Home", "Input", "Dashboard","Director Dashboard"], styles=styles)
    return tab

def input_form(df):
    st.title("Input Data for MLA Activities")

    # Date (default value is today)
    input_date = st.date_input('Date', value=date.today())

    # AC Name dropdown (from 3rd column of loaded data)
    unique_ac_names = df.iloc[:, 2].unique()
    ac_name = st.selectbox('AC Name', options=unique_ac_names)

    # Name of person
    person_name = st.text_input('ACM Name')

    # Renamed Issues to Escalation dropdown with multiple selection
    escalation_options = ['Disputes', 'Leader Activation', 'Joinings', 'Alliance Coordination', 'Organizational Issue','Governance Issue','STC Team coordination with Party']
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

    # Button to submit the data
    if st.button('Submit'):
        # Prepare the data for the CSV, one row for each escalation
        rows = []
        for escalation_detail in escalation_details:
            row = {
                'Date': input_date,
                'AC Name': ac_name,
                'Person Name': person_name,
                'Escalation': escalation_detail['Escalation'],
                'Escalation Detail': escalation_detail['Escalation Detail'],
                'Escalation Level': escalation_detail['Escalation Level'],
                'Issue Raised To': escalation_detail['Issue Raised To'],
                'Zone Response':'',
                'Comment':'',
                'Director Response':'',
                'Director Comment':''
            }
            rows.append(row)

        # Convert rows into DataFrame
        df_new = pd.DataFrame(rows)

        # Static file name for saving the data
        file_name = "mla_activities.csv"

        # Check if the CSV file already exists, and if so, append data
        if os.path.exists(file_name):
            df_existing = pd.read_csv(file_name)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(file_name, index=False)
        else:
            df_new.to_csv(file_name, index=False)

        st.success(f"Data successfully saved to {file_name}")

def load_ac_list():
    return pd.read_csv('118_AC_list.csv')

def load_mla_activities():
    return pd.read_csv('mla_activities.csv')

def update_mla_activities(df):
    df.to_csv('mla_activities.csv', index=False)

def display_dashboard():
    st.title("Field Team Dashboard")

    # Load data
    ac_list = load_ac_list()
    mla_activities = load_mla_activities()

    # Zone Selection
    unique_zones = ac_list['Zone'].unique()
    selected_zone = st.selectbox('Select Zone', options=unique_zones)

    # Filter AC Names based on selected Zone
    filtered_ac_names = ac_list[ac_list['Zone'] == selected_zone]['AC Name'].unique()
    st.write(f"Showing data for Zone: {selected_zone} (AC Names: {', '.join(filtered_ac_names)})")

    # Filter mla_activities based on the selected Zone
    filtered_activities = mla_activities[mla_activities['AC Name'].isin(filtered_ac_names)]

    ### Summary Table: Total Escalations & Status Breakdown
    st.markdown("## Escalation Summary")

    summary_data = {
        "Total Escalations": filtered_activities['Escalation'].count(),
        "Pass": filtered_activities[filtered_activities['Zone Response'] == 'Pass'].shape[0],
        "Reject": filtered_activities[filtered_activities['Zone Response'] == 'Reject'].shape[0],
        "Hold": filtered_activities[filtered_activities['Zone Response'] == 'Hold'].shape[0],
        "Remaining": filtered_activities['Zone Response'].isna().sum()
    }

    st.write(pd.DataFrame([summary_data]))

    # Subcategories of escalations
    categories = ['Disputes', 'Leader Activation', 'Joinings', 'Alliance Coordination', 'Organizational Issue','Governance Issue','STC Team coordination with Party']
    category_summary = []

    for category in categories:
        cat_data = filtered_activities[filtered_activities['Escalation'] == category]
        category_summary.append({
            'Category': category,
            'Total': cat_data.shape[0],
            'Pass': cat_data[cat_data['Zone Response'] == 'Pass'].shape[0],
            'Reject': cat_data[cat_data['Zone Response'] == 'Reject'].shape[0],
            'Hold': cat_data[cat_data['Zone Response'] == 'Hold'].shape[0],
            'Remaining': cat_data['Zone Response'].isna().sum()
        })

    st.table(pd.DataFrame(category_summary))

    ### Alert Level Table
    st.markdown("## Alert Level Summary")

    alert_levels = ['Alert', 'Mid Alert', 'Normal']
    alert_summary = []

    for level in alert_levels:
        level_data = filtered_activities[filtered_activities['Escalation Level'] == level]
        alert_summary.append({
            'Level': level,
            'Total': level_data.shape[0],
            'Pass': level_data[level_data['Zone Response'] == 'Pass'].shape[0],
            'Reject': level_data[level_data['Zone Response'] == 'Reject'].shape[0],
            'Hold': level_data[level_data['Zone Response'] == 'Hold'].shape[0],
            'Remaining': level_data['Zone Response'].isna().sum()
        })

    st.table(pd.DataFrame(alert_summary))

    ### Database Section in Table Format
    ### Database Section in Table Format
    st.markdown("## Database")
    if not filtered_activities.empty:
        # Initialize empty values for 'Zone Response' and 'Comment' if not present
        filtered_activities['Zone Response'] = filtered_activities['Zone Response'].fillna('')
        filtered_activities['Comment'] = filtered_activities['Comment'].fillna('')

        # Create a list to hold updated rows
        updated_rows = []

        # Display the table headers with aligned columns
        st.markdown(
            """
            <style>
            .align-table th {
                text-align: left;
                font-weight: bold;
                padding: 4px 8px;
            }
            .align-table td {
                padding: 4px 8px;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        
        # Create table headers
        st.markdown(
            """
            <table class="align-table">
                <thead>
                    <tr>
                        <th>AC Name</th>
                        <th>Escalation</th>
                        <th>Escalation Detail</th>
                        <th>Escalation Level</th>
                        <th>Zone Response</th>
                        <th>Comment</th>
                        <th>Issue Raised To</th>
                    </tr>
                </thead>
                <tbody>
            """, 
            unsafe_allow_html=True
        )

        # Loop through each row and create the table body with inputs
        for idx, row in filtered_activities.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1.5, 1, 1, 1.5, 1])
            Director_Response, Director_Comment=row['Director Response'],row['Director Comment']
            # Static columns
            col1.write(row['AC Name'])
            col2.write(row['Escalation'])
            col3.write(row['Escalation Detail'])
            col4.write(row['Escalation Level'])

            # Editable 'Zone Response' Dropdown
            new_zone_response = col5.selectbox(
                '',
                options=[row['Zone Response'], 'Pass', 'Reject', 'Hold'],
                index=0 if row['Zone Response'] == '' else ['Pass', 'Reject', 'Hold'].index(row['Zone Response']),
                key=f'zone_response_{idx}'
            )

            # Editable 'Comment' Text Input
            new_comment = col6.text_input(
                '',
                value=row['Comment'],
                key=f'comment_{idx}'
            )

            # Static column
            col7.write(row['Issue Raised To'])

            # Append updated rows back to the dataframe
            updated_rows.append({
                'AC Name': row['AC Name'],
                'Escalation': row['Escalation'],
                'Escalation Detail': row['Escalation Detail'],
                'Escalation Level': row['Escalation Level'],
                'Zone Response': new_zone_response,
                'Comment': new_comment,
                'Issue Raised To': row['Issue Raised To'],
                'Director Response': Director_Response,
                'Director Comment': Director_Comment
            })

        st.markdown("</tbody></table>", unsafe_allow_html=True)

        # Convert updated rows back into a DataFrame
        df_updated = pd.DataFrame(updated_rows)

        # Save button to update the CSV file
        if st.button("Update Database"):
            update_mla_activities(df_updated)
            st.success("Database updated successfully!")

    else:
        st.warning("No data available for the selected Zone.")

def display_director_dashboard():
    st.title("Director Dashboard")

    # Load data
    ac_list = load_ac_list()
    mla_activities = load_mla_activities()

    # Zone Selection
    unique_zones = ac_list['Zone'].unique()
    selected_zone = st.selectbox('Select Zone', options=unique_zones)

    # Filter AC Names based on selected Zone
    filtered_ac_names = ac_list[ac_list['Zone'] == selected_zone]['AC Name'].unique()

    # Filter mla_activities based on the selected Zone and 'Pass' Zone Response
    passed_activities = mla_activities[(mla_activities['AC Name'].isin(filtered_ac_names)) & (mla_activities['Zone Response'] == 'Pass')]

    st.write(f"Showing data for Zone: {selected_zone} (AC Names: {', '.join(filtered_ac_names)})")
    
    # st.markdown("## Escalation Summary")

    # summary_data = {
    #     "Total Escalations": filtered_activities['Escalation'].count(),
    #     "Pass": filtered_activities[filtered_activities['Zone Response'] == 'Pass'].shape[0],
    #     "Reject": filtered_activities[filtered_activities['Zone Response'] == 'Reject'].shape[0],
    #     "Hold": filtered_activities[filtered_activities['Zone Response'] == 'Hold'].shape[0],
    #     "Remaining": filtered_activities['Zone Response'].isna().sum()
    # }

    # st.write(pd.DataFrame([summary_data]))
    ### Escalation Summary Table: Total Escalations & Status Breakdown
    st.markdown("## Escalation Summary")

    summary_data = {
        "Total Escalations": passed_activities['Escalation'].count(),
        "Pass": passed_activities[passed_activities['Director Response'] == 'Pass'].shape[0],
        "Reject": passed_activities[passed_activities['Director Response'] == 'Reject'].shape[0],
        "Hold": passed_activities[passed_activities['Director Response'] == 'Hold'].shape[0],
        "Remaining": passed_activities['Director Response'].isna().sum()
    }

    st.write(pd.DataFrame([summary_data]))

    # Subcategories of escalations
    categories = ['Disputes', 'Leader Activation', 'Joinings', 'Alliance Coordination', 'Organizational Issue', 'Governance Issue', 'STC Team coordination with Party']
    category_summary = []

    for category in categories:
        cat_data = passed_activities[passed_activities['Escalation'] == category]
        category_summary.append({
            'Category': category,
            'Total': cat_data.shape[0],
            'Pass': cat_data[cat_data['Director Response'] == 'Pass'].shape[0],
            'Reject': cat_data[cat_data['Director Response'] == 'Reject'].shape[0],
            'Hold': cat_data[cat_data['Director Response'] == 'Hold'].shape[0],
            'Remaining': cat_data['Director Response'].isna().sum()
        })

    st.table(pd.DataFrame(category_summary))

    ### Alert Level Table
    st.markdown("## Alert Level Summary")

    alert_levels = ['Alert', 'Mid Alert', 'Normal']
    alert_summary = []

    for level in alert_levels:
        level_data = passed_activities[passed_activities['Escalation Level'] == level]
        alert_summary.append({
            'Level': level,
            'Total': level_data.shape[0],
            'Pass': level_data[level_data['Director Response'] == 'Pass'].shape[0],
            'Reject': level_data[level_data['Director Response'] == 'Reject'].shape[0],
            'Hold': level_data[level_data['Director Response'] == 'Hold'].shape[0],
            'Remaining': level_data['Director Response'].isna().sum()
        })

    st.table(pd.DataFrame(alert_summary))

    # Add a dropdown to select an AC Name from the filtered activities in the selected Zone
    st.markdown("## Select AC Name")
    unique_ac_names = passed_activities['AC Name'].unique()
    selected_ac_name = st.selectbox('Select AC Name', options=unique_ac_names)

    # Filter data based on the selected AC Name
    filtered_ac_activities = passed_activities[passed_activities['AC Name'] == selected_ac_name]

    # Display filtered data
    st.markdown(f"## Database for AC: {selected_ac_name}")

    if not filtered_ac_activities.empty:
        # Initialize empty values for 'Director Response' and 'Director Comment' if not present
        filtered_ac_activities['Director Response'] = filtered_ac_activities['Director Response'].fillna('')
        filtered_ac_activities['Director Comment'] = filtered_ac_activities['Director Comment'].fillna('')

        # Create a list to hold updated rows
        updated_rows = []

        # Display the table headers with aligned columns
        st.markdown(
            """
            <style>
            .align-table th {
                text-align: left;
                font-weight: bold;
                padding: 4px 8px;
            }
            .align-table td {
                padding: 4px 8px;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        
        # Create table headers
        st.markdown(
            """
            <table class="align-table">
                <thead>
                    <tr>
                        <th>AC Name</th>
                        <th>Escalation</th>
                        <th>Escalation Detail</th>
                        <th>Escalation Level</th>
                        <th>Zone Response</th>
                        <th>Zone Comment</th>
                        <th>Director Response</th>
                        <th>Director Comment</th>
                        <th>Issue Raised To</th>
                    </tr>
                </thead>
                <tbody>
            """, 
            unsafe_allow_html=True
        )

        # Loop through each row and create the table body with inputs
        for idx, row in filtered_ac_activities.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1, 1, 1.5, 1, 1, 1.5, 1, 1.5, 1])

            # Static columns
            col1.write(row['AC Name'])
            col2.write(row['Escalation'])
            col3.write(row['Escalation Detail'])
            col4.write(row['Escalation Level'])
            col5.write(row['Zone Response'])  # Static Zone Response
            col6.write(row['Comment'])        # Static Zone Comment

            # Editable 'Director Response' Dropdown
            new_director_response = col7.selectbox(
                '',
                options=['', 'Pass', 'Reject', 'Hold'],
                index=0 if row['Director Response'] == '' else ['Pass', 'Reject', 'Hold'].index(row['Director Response']),
                key=f'director_response_{idx}'
            )

            # Editable 'Director Comment' Text Input
            new_director_comment = col8.text_input(
                '',
                value=row['Director Comment'],
                key=f'director_comment_{idx}'
            )

            # Static column for 'Issue Raised To'
            col9.write(row['Issue Raised To'])

            # Append updated rows back to the dataframe
            updated_rows.append({
                'AC Name': row['AC Name'],
                'Escalation': row['Escalation'],
                'Escalation Detail': row['Escalation Detail'],
                'Escalation Level': row['Escalation Level'],
                'Zone Response': row['Zone Response'],
                'Comment': row['Comment'],
                'Director Response': new_director_response,
                'Director Comment': new_director_comment,
                'Issue Raised To': row['Issue Raised To']
            })

        st.markdown("</tbody></table>", unsafe_allow_html=True)

        # Convert updated rows back into a DataFrame
        df_updated = pd.DataFrame(updated_rows)

        # Save button to update the CSV file
        if st.button("Update Director Responses"):
            update_mla_activities(df_updated)
            st.success("Director responses updated successfully!")

    else:
        st.warning(f"No data available for the selected AC Name: {selected_ac_name}.")

# if __name__ == "__main__":
#     display_dashboard()

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

    elif tab=="Director Dashboard":
        display_director_dashboard()    

if __name__ == "__main__":
    main()