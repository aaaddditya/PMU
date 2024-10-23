import streamlit as st
import pandas as pd
import os
from datetime import datetime,date
import numpy as np
from streamlit_navigation_bar import st_navbar
from PIL import Image
import time

st.set_page_config(
    layout="wide",
)
# st._config.set_option(backgroundColor:'')


# Function to check login credentials
def authenticate_user(email, password, user_data):
    user_row = user_data[(user_data['email'] == email) & (user_data['password'] == password)]
    if not user_row.empty:
        return user_row.iloc[0]['userName'], user_row.iloc[0]['roles']
    return None, None

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['userName'] = ''
    st.session_state['role'] = ''

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = ''
    if 'role' not in st.session_state:
        st.session_state['role'] = ''
    if 'mobile_view' not in st.session_state:
        st.session_state['mobile_view'] = False
def change_mobile_view():
    if st.session_state['mobile_view']:
        st.session_state['mobile_view']=False
    else:
        st.session_state['mobile_view']=True

def login_page():
    st.markdown("<h1 style='color:#0897ff;text-align:center'>2024 AE Escalation</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center'>Login Page</h3>", unsafe_allow_html=True)

    # Create a rectangular box for the login form
    with st.container():
        # st.markdown(
        #     """
        #     <div style="border: 2px solid #0897ff; border-radius: 10px; padding: 20px; width: 300px; margin: auto;">
        #     """, unsafe_allow_html=True
        # )
        email = st.text_input("Email", key='email', max_chars=50, placeholder="Enter your email")
        password = st.text_input("Password", type="password", key='password', placeholder="Enter your password")

        if st.button("Login"):
            try:
                password = int(password)
            except ValueError:
                st.error("Password must be a number.")
                return
            
            user_data = pd.read_csv('userdata.csv')
            userName, role = authenticate_user(email, password, user_data)
            if userName:
                st.session_state['logged_in'] = True
                st.session_state['userName'] = userName
                st.session_state['role'] = role
                st.success(f"Welcome, {userName}!")
            else:
                st.error("Invalid email or password")
        
        st.markdown("</div>", unsafe_allow_html=True)


# Function for Home page

# def load_data(selected_date, selected_ac_name):
#     file_name = f"{selected_date.strftime('%d%m%Y')}.csv"
#     if os.path.exists(file_name):
#         try:
#             df = pd.read_csv(file_name)
#             if df.empty:
#                 st.warning("The file is empty. No data available.")
#                 return None
#             # Filter the data by AC Name
#             filtered_df = df[df['AC Name'] == selected_ac_name]
#             return filtered_df
#         except pd.errors.EmptyDataError:
#             st.error(f"The file {file_name} is empty.")
#             return None
#     else:
#         st.warning(f"No data file found for the date {selected_date.strftime('%d%m%Y')}.")
#         return None

# Function to load AC data from 118_AC_list.csv
def load_ac_data(ac_name):
    ac_data = pd.read_csv('118_AC_list.csv')
    # Filter the data for the selected AC Name
    filtered_ac_data = ac_data[ac_data['AC Name'] == ac_name]
    if not filtered_ac_data.empty:
        return filtered_ac_data.iloc[0]  # Return the first matching row
    else:
        return None
    
# def load_ddmm_data(selected_date, ac_name):
#     file_name = f"{selected_date.strftime('%d%m%Y')}.csv"
#     if os.path.exists(file_name):
#         df = pd.read_csv(file_name)
#         # Filter the data by AC Name
#         filtered_df = df[df['AC Name'] == ac_name]
#         return filtered_df
#     else:
#         return None
        
# Navbar Functionality (Tab navigation)
def display_navbar():
    # Define the tabs
    # tabs = ["Home", "Input", "Dashboard", "Director Dashboard"]
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
    if st.session_state['role'] == "user":
        tab=st_navbar(["Home", "Input","logout"], styles=styles)
    elif st.session_state['role'] == "user1":   
        tab=st_navbar(["Home", "Dashboard","logout"], styles=styles)
    elif st.session_state['role'] == "user2": 
        tab=st_navbar(["Home", "Director Dashboard","logout"], styles=styles)
    elif st.session_state['role'] == "user3":    
        tab=st_navbar(["Home", "Input","Dashboard","Director Dashboard","logout"], styles=styles)
    else:
        tab=st_navbar(["Home"], styles=styles)
    # st.write(st.session_state)   
    return tab

def input_form(df):
    st.title("Input Data for AC Escalation")

    # Date (default value is today)
    input_date=st.date_input('Date', value=date.today())
    current_time = datetime.now().time()

# Combine the date and current time
    combined_datetime = datetime.combine(input_date, current_time)

    st.write(combined_datetime)

    # AC Name dropdown (from 3rd column of loaded data)
    unique_ac_names = df.iloc[:, 2].unique()
    ac_name = st.selectbox('AC Name', options=sorted(unique_ac_names))

    # Name of person
    person_name = st.text_input('ACM Name')

    # Renamed Issues to Escalation dropdown with multiple selection
    escalation_options = ['Disputes', 'Leader Activation', 'Joinings', 'Alliance Coordination', 'Organizational Issue','Governance Issue','STC Team coordination with Party']
    selected_escalations = st.multiselect('Escalation', options=escalation_options)

    # For each Escalation, we ask for Escalation Detail, Escalation Level, and Issue Raised To
    escalation_details = []
    for escalation in selected_escalations:
        st.markdown(f"### Escalation Details for {escalation}")

        intro=st.text_input(f"{escalation} detail in one line")
        # Escalation Detail text input
        detail = st.text_area(f"Escalation Detail for {escalation}")
        
        # Escalation Level
        level = st.selectbox(f'Escalation Level for {escalation}', options=['Low', 'Medium', 'High'])
        
        # Issue Raised To
        raised_to = st.selectbox(f'Issue Raised to for {escalation}', options=['Anurag Saxena', 'Anant Tiwari', 'Alimpan Banerjee','Sanjay More (Party, Dispute)','Bhausaheb Choudhary (Party, Joining)', 'Ashishish Kulkarni (Party, Alliance Coordination)','Sanjay More (Party, Alliance Coordination)','Sanjay More (Party, Organizational Issue)','Sandeep Shinde (Party, Governance Issue)','Sachin Joshi (Party, Governance Issue)','Bhausaheb Choudhary (Party, STC Team coordination with Party)'])
        
        # Store all details in a dictionary for this escalation
        escalation_details.append({
            'Escalation': escalation,
            'Escalation Intro': intro,
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
                'Date': combined_datetime,
                'Person Name': person_name,
                'AC Name': ac_name,               
                'Escalation': escalation_detail['Escalation'],
                'Escalation Intro': escalation_detail['Escalation Intro'],
                'Escalation Detail': escalation_detail['Escalation Detail'],
                'Escalation Level': escalation_detail['Escalation Level'],
                'Zone Response':'',
                'Comment':'',
                'Director Response':'',
                'Director Comment':'',
                'Issue Raised To': escalation_detail['Issue Raised To']
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
    df13=pd.read_csv('user1.csv')
    temp= df13[df13['userName']==st.session_state['userName']]['Zone'].values
    if len(temp):
        
        selected_zone = st.selectbox('Select Zone', options=temp)
    else:
        selected_zone = st.selectbox('Select Zone', options=unique_zones)

    # Filter AC Names based on selected Zone
    filtered_ac_names = ac_list[ac_list['Zone'] == selected_zone]['AC Name'].unique()
    st.write(f"Showing data for Zone: {selected_zone} (AC Names: {', '.join(filtered_ac_names)})")

    # Filter mla_activities based on the selected Zone
    filtered_activities = mla_activities[mla_activities['AC Name'].isin(filtered_ac_names)]
    st.write(filtered_activities)
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

    alert_levels = ['Low', 'Medium', 'High']
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
    st.checkbox(
        "Mobile View",
        # value=st.session_state.mobile_view,
        # key='mobile_view',
        on_change=change_mobile_view  # Call the function when the checkbox is changed
)
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
        
       
        flag = True
        updated_rows = []
        mobile_view=True
        for idx, row in filtered_activities.iterrows():
            # Dynamically adjust columns for desktop vs mobile view
            if  st.session_state['mobile_view']:
                # Mobile view: use fewer columns and show details in an expander
                with st.expander(f"{row['AC Name']} , {row['Zone Response']} - Escalation Details"):
                    col1, col2 = st.columns([1, 2])
                    col1.write(f"Escalation: {row['Escalation']}")
                    col2.write(f"Level: {row['Escalation Level']}")
                    st.write(f"Escalation Intro: {row['Escalation Intro']}")
                    st.write(f"Escalation Detail: {row['Escalation Detail']}")
                    st.write(f"Issue Raised To: {row['Issue Raised To']}")


                    # Editable Zone Response and Comment in mobile view
                    new_zone_response = st.selectbox(
                        'Zone Response',
                        options=['','Pass', 'Reject', 'Hold'],
                        index=0 if row['Zone Response'] == '' else ['','Pass', 'Reject', 'Hold'].index(row['Zone Response']),
                        key=f'zone_response_{idx}'
                    )
                    
                    new_comment = st.text_input(
                        'Comment',
                        value=row['Comment'],
                        key=f'comment_{idx}'
                    )

            else:
                # Desktop view: retain multiple columns for richer details
                col1, col2, col3, col4, col5, col6, col7 ,col8= st.columns([1, 1, 1.5, 1.5, 1, 1, 1.5, 1,])

                # Static columns
                if flag:
                    col1.write('AC Name')
                    col2.write('Escalation')
                    col3.write('Escalation Intro')
                    col4.write('Escalation Detail')
                    col5.write('Escalation Level')
                    col6.write('Zone Response')
                    col7.write('Comment')
                    col8.write('Issue Raised To')
                    flag = False

                col1.write(row['AC Name'])
                col2.write(row['Escalation'])
                col3.write(row['Escalation Intro'])
                col4.write(row['Escalation Detail'])
                col5.write(row['Escalation Level'])

                # Editable Zone Response Dropdown for desktop view
                new_zone_response = col6.selectbox(
                    '',
                    options=['', 'Pass', 'Reject', 'Hold'],
                    index=0 if row['Zone Response'] == '' else ['','Pass', 'Reject', 'Hold'].index(row['Zone Response']),
                    key=f'zone_response_{idx}'
                )
                # Editable Comment Text Input
                new_comment = col7.text_input(
                    '',
                    placeholder=row['Comment'],
                    value=row['Comment'],
                    key=f'comment_{idx}'
                )

                # Static column for Issue Raised To
                col8.write(row['Issue Raised To'])

            # Append updated rows back to the dataframe
            updated_rows.append({
                'Date': row['Date'],                
                'Person Name': row['Person Name'],
                'AC Name': row['AC Name'],
                'Escalation': row['Escalation'],
                'Escalation Intro': row['Escalation Intro'],
                'Escalation Detail': row['Escalation Detail'],
                'Escalation Level': row['Escalation Level'],
                'Zone Response': new_zone_response,
                'Comment': new_comment,               
                'Director Response': row['Director Response'],
                'Director Comment': row['Director Comment'],
                'Issue Raised To': row['Issue Raised To']
            })

        st.markdown("</tbody></table>", unsafe_allow_html=True)

        # Convert updated rows back into a DataFrame

        
        

        # Save button to update the CSV file
        if st.button("Update Database"):
            # df_updated.to_csv('mla_activities.csv', index=False)

            df = pd.read_csv('mla_activities.csv')


            # Loop through the updated_rows list
            for updated_row in updated_rows:
                # Define the conditions
                date_condition = updated_row['Date']
                name_condition = updated_row['Person Name']
                
                # Update the DataFrame where conditions match
                df.loc[(df['Date'] == date_condition) & (df['Person Name'] == name_condition), 'Zone Response'] = updated_row['Zone Response']
                df.loc[(df['Date'] == date_condition) & (df['Person Name'] == name_condition), 'Comment'] = updated_row['Comment']

            # Save the updated DataFrame back to the CSV file
            df.to_csv('mla_activities.csv', index=False)

            st.success("Database updated successfully!")
            time.sleep(1)
            st.rerun()

    else:
        st.warning("No data available for the selected Zone.")

def display_director_dashboard():
    st.title("Director Dashboard")

    # Load data
    ac_list = load_ac_list()
    mla_activities = load_mla_activities()
    
    st.markdown("## State Summary")
    filtered_activities1=mla_activities[(mla_activities['Zone Response'] == 'Pass')]
    summary_data = {
        "Total Escalations": filtered_activities1['Escalation'].count(),
        "Resolved": filtered_activities1[filtered_activities1['Director Response'] == 'Resolved'].shape[0],
        "Cannot be Resolved": filtered_activities1[filtered_activities1['Director Response'] == 'Cannot be Resolved'].shape[0],
        "In Discussion": filtered_activities1[filtered_activities1['Director Response'] == 'In Discussion'].shape[0],
        "Pending": filtered_activities1['Director Response'].isna().sum()
    }
    
    st.write(pd.DataFrame([summary_data]))
    # Zone Selection
    unique_zones = ac_list['Zone'].unique()
    selected_zone = st.selectbox('Select Zone', options=unique_zones)

    # Filter AC Names based on selected Zone
    filtered_ac_names = ac_list[ac_list['Zone'] == selected_zone]['AC Name'].unique()
    
    # Filter mla_activities based on the selected Zone and 'Pass' Zone Response
    passed_activities = mla_activities[(mla_activities['AC Name'].isin(filtered_ac_names)) & (mla_activities['Zone Response'] == 'Pass')]

    st.write(f"Showing data for Zone: {selected_zone} (AC Names: {', '.join(filtered_ac_names)})")
    
    
    ### Escalation Summary Table: Total Escalations & Status Breakdown
    st.markdown("## Escalation Summary")

    summary_data = {
        "Total Escalations": passed_activities['Escalation'].count(),
        "Resolved": passed_activities[passed_activities['Director Response'] == 'Resolved'].shape[0],
        "Cannot be Resolved": passed_activities[passed_activities['Director Response'] == 'Cannot be Resolved'].shape[0],
        "In Discussion": passed_activities[passed_activities['Director Response'] == 'In Discussion'].shape[0],
        "Pending": passed_activities['Director Response'].isna().sum()
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
            'Resolved': cat_data[cat_data['Director Response'] == 'Resolved'].shape[0],
            'Cannot be Resolved': cat_data[cat_data['Director Response'] == 'Cannot be Resolved'].shape[0],
            'In Discussion': cat_data[cat_data['Director Response'] == 'In Discussion'].shape[0],
            'Pending': cat_data['Director Response'].isna().sum()
        })

    st.table(pd.DataFrame(category_summary))

    ### Alert Level Table
    st.markdown("## Alert Level Summary")

    alert_levels = ['Low', 'Medium', 'High']
    alert_summary = []

    for level in alert_levels:
        level_data = passed_activities[passed_activities['Escalation Level'] == level]
        alert_summary.append({
            'Level': level,
            'Total': level_data.shape[0],
            'Resolved': level_data[level_data['Director Response'] == 'Resolved'].shape[0],
            'Cannot be Resolved': level_data[level_data['Director Response'] == 'Cannot be Resolved'].shape[0],
            'In Discussion': level_data[level_data['Director Response'] == 'In Discussion'].shape[0],
            'Pending': level_data['Director Response'].isna().sum()
        })

    st.table(pd.DataFrame(alert_summary))

    # Add a dropdown to select an AC Name from the filtered activities in the selected Zone
    st.markdown("## Select AC Name")
    unique_ac_names = passed_activities['AC Name'].unique()
    # st.write(passed_activities.head(2))
    selected_ac_name = st.selectbox('Select AC Name', options=unique_ac_names)

    st.markdown("## Select Issue Raised to Name")
    unique_issue_names = passed_activities['Issue Raised To'].unique()
    # st.write(passed_activities.head(2))
    selected_issue_name = st.selectbox('Select Issue Name', options=unique_issue_names)

    # Filter data based on the selected AC Name
    filtered_ac_activities = passed_activities[(passed_activities['AC Name'] == selected_ac_name) & (passed_activities['Issue Raised To'] == selected_issue_name)]

    
    # Display filtered data

    st.markdown(f"## Database for AC: {selected_ac_name}")
    st.checkbox(
    "Mobile View",
    # value=st.session_state.mobile_view,
    # key='mobile_view',
    on_change=change_mobile_view  # Call the function when the checkbox is changed
)
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

        if not st.session_state.mobile_view:
            flag=True
            # Loop through each row and create the table body with inputs for desktop view
            for idx, row in filtered_ac_activities.iterrows():
                col1, col2, col3, col4, col5, col6, col7, col8, col9 ,col10= st.columns([1, 1, 1.5, 1.5, 1, 1, 1.5, 1, 1.5, 1])

                if flag:
                    col1.write('AC Name')
                    col2.write('Escalation')
                    col3.write('Escalation Intro')
                    col4.write('Escalation Detail')
                    col5.write('Escalation Level')
                    col6.write('Zone Response')
                    col7.write('Comment')
                    col8.write('Director Response')
                    col9.write('Director Comment')
                    col10.write('Issue Raised To')
                    flag = False

                # Static columns
                col1.write(row['AC Name'])
                col2.write(row['Escalation'])
                col3.write(row['Escalation Intro'])
                col4.write(row['Escalation Detail'])
                col5.write(row['Escalation Level'])
                col6.write(row['Zone Response'])  # Static Zone Response
                col7.write(row['Comment'])        # Static Zone Comment

                # Editable 'Director Response' Dropdown
                new_director_response = col8.selectbox(
                    '',
                    options=['','Resolved', 'Cannot be Resolved', 'In Discussion'],
                    index=0 if row['Director Response'] == '' else ['','Resolved', 'Cannot be Resolved', 'In Discussion'].index(row['Director Response']),
                    key=f'director_response_{idx}'
                )

                # Editable 'Director Comment' Text Input
                new_director_comment = col9.text_input(
                    '',
                    value=row['Director Comment'],
                    key=f'director_comment_{idx}'
                )

                # Static column for 'Issue Raised To'
                col10.write(row['Issue Raised To'])

                # Append updated rows back to the dataframe
                updated_rows.append({
                    'Date': row['Date'],                
                    'Person Name': row['Person Name'],
                    'AC Name': row['AC Name'],
                    'Escalation': row['Escalation'],
                    'Escalation Intro': row['Escalation Intro'],
                    'Escalation Detail': row['Escalation Detail'],
                    'Escalation Level': row['Escalation Level'],
                    'Zone Response': row['Zone Response'],
                    'Comment': row['Comment'],
                    'Director Response': new_director_response,
                    'Director Comment': new_director_comment,
                    'Issue Raised To': row['Issue Raised To']
                })

            st.markdown("</tbody></table>", unsafe_allow_html=True)

        else:
            
            mobile_view=True
            # Mobile view: use fewer columns and show details in expanders
            for idx, row in filtered_ac_activities.iterrows():
                if  st.session_state['mobile_view']:
                    with st.expander(f"{row['AC Name']} , {row['Director Response']} , {row['Issue Raised To']} - Escalation Details"):
                        col1, col2 = st.columns([1, 2])
                        col1.write(f"Escalation: {row['Escalation']}")
                        col2.write(f"Level: {row['Escalation Level']}")
                        st.write(f"Escalation Intro: {row['Escalation Intro']}")
                        st.write(f"Escalation Detail: {row['Escalation Detail']}")
                        st.write(f"Issue Raised To: {row['Issue Raised To']}")

                        # Editable Zone Response and Comment in mobile view
                        new_director_response = st.selectbox(
                            'Director Response',
                            options=['', 'Resolved', 'Cannot be Resolved', 'In Discussion'],
                            index=0 if row['Director Response'] == '' else ['','Resolved', 'Cannot be Resolved', 'In Discussion'].index(row['Director Response']),
                            key=f'director_response_{idx}'
                        )

                        new_director_comment = st.text_input(
                            'Director Comment',
                            value=row['Director Comment'],
                            key=f'director_comment_{idx}'
                        )

                        # Append updated rows back to the dataframe
                        updated_rows.append({
                            'Date': row['Date'],                
                            'Person Name': row['Person Name'],
                            'AC Name': row['AC Name'],
                            'Escalation': row['Escalation'],
                            'Escalation Intro': row['Escalation Intro'],
                            'Escalation Detail': row['Escalation Detail'],
                            'Escalation Level': row['Escalation Level'],
                            'Zone Response': row['Zone Response'],
                            'Comment': row['Comment'],                           
                            'Director Response': new_director_response,
                            'Director Comment': new_director_comment,
                            'Issue Raised To': row['Issue Raised To'],
                        })

        # Convert updated rows back into a DataFrame
        df_updated = pd.DataFrame(updated_rows)

        # Save button to update the CSV file
        if st.button("Update Director Responses"):
            df = pd.read_csv('mla_activities.csv')

            # Example updated_rows list with new values for Director Response and Comment
           

            # Loop through the updated_rows list
            for updated_row in updated_rows:
                date_condition = updated_row['Date']
                name_condition = updated_row['Person Name']
                
                # Update the DataFrame where conditions match
                df.loc[(df['Date'] == date_condition) & (df['Person Name'] == name_condition), 'Director Response'] = updated_row['Director Response']
                df.loc[(df['Date'] == date_condition) & (df['Person Name'] == name_condition), 'Director Comment'] = updated_row['Director Comment']

            # Save the updated DataFrame back to the CSV file
            df.to_csv('mla_activities.csv', index=False)


            st.success("Director responses updated successfully!")
            time.sleep(1)
            st.rerun()

    else:
        st.warning(f"No data available for the selected AC Name: {selected_ac_name}.")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user'] = ''
    st.session_state['role'] = ''
    st.rerun()

# if st.session_state['logged_in']:
#     logout_button=st.button("logout")

#     if logout_button:
#         logout()

def render_navigation():
    if st.session_state['role'] == 'user':
        st.sidebar.button("Home", on_click=home_page)
        st.sidebar.button("Input", on_click=input_form)
    elif st.session_state['role'] == 'user1':
        st.sidebar.button("Home", on_click=home_page)
        st.sidebar.button("Dashboard", on_click=display_dashboard)
    elif st.session_state['role'] == 'user2':
        st.sidebar.button("Home", on_click=home_page)
        st.sidebar.button("Director Dashboard", on_click=display_director_dashboard)
    elif st.session_state['role'] == 'user3':
        st.sidebar.button("Home", on_click=home_page)
        st.sidebar.button("Input", on_click=input_form)
        st.sidebar.button("Dashboard", on_click=display_dashboard)
        st.sidebar.button("Director Dashboard", on_click=display_director_dashboard)

def home_page():
    st.markdown("<div class='blank-screen'></div>", unsafe_allow_html=True)
    # Add custom CSS for fade-in text animation from a blank screen
    st.markdown(
        """
        <style>
        /* Blank white screen initially */
        .blank-screen {
            background-color: white;
            height: 10vh;  /* Adjust height to cover the required area */
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* Fade-in effect for the text */
        .fade-in-text {
            opacity: 0;
            animation: fadeInText 3s ease-in forwards; /* 3-second fade-in animation */
        }

        @keyframes fadeInText {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Blank screen for a moment (before the text appears)

    # Wait for the blank screen (optional, if you want a pause before the text)
    time.sleep(0)

    # Display Home page text with fade-in animation
    st.markdown(
        f"""
        <div class="fade-in-text" style="text-align: center; margin-top: -50px;">
            <h1>Home</h1>
            <h2><strong>Welcome, {st.session_state['userName']}</strong></h2>
            <p>Welcome to the 2024 Maharashtra Assembly Election Dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.session_state.get('userName') == "Aditya Malhotra":
        st.write(pd.read_csv('mla_activities.csv'))
        st.download_button(
            label="Download data as CSV",
            data=pd.read_csv('mla_activities.csv').to_csv(index=False),
            file_name="mla_activities.csv",
            mime="text/csv",
        )



if not st.session_state['logged_in']:
    login_page()  # Show login page if not logged in
# else:
#     # render_navigation()  # Show the navigation bar after login
#     home_page()      
# if __name__ == "__main__":
#     display_dashboard()

# Home Page Functionality
    # new_title = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">Aditya</p>'
    # st.markdown(new_title, unsafe_allow_html=True)
# Main Streamlit App

def main():
    # Display the navigation bar and switch between tabs
    # page = st_navbar(["Home", "Input", "Dashboard"])
    init_session_state() 
    if st.session_state['logged_in']:

         
        
        tab = display_navbar()
        # st.write(st.session_state)
        # Load data for input formstreamlit 
        df = pd.read_csv('288_MLA.csv')

        # if 'logged_in' not in st.session_state:
        #     st.session_state['logged_in'] = False

        # if not st.session_state['logged_in']:
        #     login()
        # else:
        #     st.sidebar.title("Navigation")
        #     role_based_menu()

        #     if st.sidebar.button("Logout"):
        #         logout()

            # Page Rendering
            # page = st.sidebar.radio("Select Page", ['Home', 'Input Page', 'Dashboard', 'Director Dashboard'])

            
        # Home tab
        if tab == "Home":
            home_page()

        # Input tab
        elif tab == 'Input' and (st.session_state['role'] in ['user', 'user3']):
            input_form(df)

        # Dashboard tab
        elif tab == 'Dashboard' and (st.session_state['role'] in ['user1', 'user3']):
            display_dashboard()

        elif tab=='Director Dashboard' and (st.session_state['role'] in ['user2', 'user3']):
            display_director_dashboard()    
        elif tab=="logout":
            logout()   
        # elif tab=='Mobile View':
            
        
            
                 

if __name__ == "__main__":
    main()