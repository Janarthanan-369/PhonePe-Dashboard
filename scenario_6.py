# scenario_6.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import run_query

# --- Functions for each question ---

def question_1_top_states_2022_q3():
    """Q1: Which states have the highest number of registered users in 2022 Q3?"""
    st.subheader("Top 10 States by Registered Users (2022 Q3)")
    query = """
    SELECT state, registered_users
    FROM aggregated_user
    WHERE year = 2022 AND quarter = 3
      AND (device_brand IS NULL OR device_brand = '')
    ORDER BY registered_users DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        df['registered_users_formatted'] = df['registered_users'].apply(lambda x: f"{x/1000000:.2f} M")
        fig = px.bar(
            df,
            x='state',
            y='registered_users',
            title='Highest Registered Users by State (2022 Q3)',
            labels={'state': 'State', 'registered_users': 'Number of Registered Users'},
            hover_name='state',
            custom_data=['registered_users_formatted']
        )
        fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Registered Users: %{customdata[0]}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_2_registration_trend_since_2018():
    """Q2: What is the trend of user registrations across all quarters since 2018?"""
    st.subheader("Nationwide User Registration Trend (Since 2018)")
    query = """
    SELECT
        CONCAT(year, '-Q', quarter) as period,
        SUM(registered_users) as total_registered_users
    FROM aggregated_user
    WHERE year >= 2018
      AND (device_brand IS NULL OR device_brand = '')
    GROUP BY year, quarter
    ORDER BY year, quarter;
    """
    try:
        df = run_query(query)
        fig = px.area(
            df,
            x='period',
            y='total_registered_users',
            title='Total Registered Users Over Time',
            labels={'period': 'Quarter', 'total_registered_users': 'Total Registered Users'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_3_top_pincodes_by_registration():
    """Q3: Which pin codes had the highest registrations in the last year?"""
    st.subheader("Top 10 Pincodes by Registered Users (Overall)")
    st.warning("**Note:** The `top_user_by_pincode` table does not contain time-based data. This analysis shows the top pincodes based on the overall data available.")
    query = """
    SELECT pincode, district_name, state, registeredusers
    FROM top_user_by_pincode
    ORDER BY registeredusers DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_4_new_users_by_region_2021():
    """Q4: How many new users registered in each state per quarter during 2021?"""
    st.subheader("New User Registrations per State during 2021")
    # CORRECTED QUERY
    query = """
    WITH quarterly_district_users AS (
        SELECT
            state_name, district_name, year, quarter, registered_users,
            LAG(registered_users, 1, 0) OVER (PARTITION BY state_name, district_name ORDER BY year, quarter) as prev_q_users
        FROM map_user
        WHERE year = 2021 OR (year = 2020 AND quarter = 4)
    ),
    quarterly_state_growth AS (
        SELECT
            state_name,
            CONCAT('Q', quarter) as period,
            SUM(registered_users - prev_q_users) as new_users
        FROM quarterly_district_users
        WHERE year = 2021 AND prev_q_users > 0
        GROUP BY state_name, period
    )
    SELECT * FROM quarterly_state_growth ORDER BY state_name, period;
    """
    try:
        df = run_query(query)
        fig = px.bar(
            df,
            x='state_name',
            y='new_users',
            color='period',
            barmode='group',
            title='New Users per Quarter in 2021 by State',
            labels={'state_name': 'State', 'new_users': 'Number of New Users', 'period': 'Quarter'}
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_5_district_contribution_early_2023():
    """Q5: Which districts contributed the most to registrations in early 2023?"""
    st.subheader("Top 10 Districts by New Registrations (Early 2023)")
    st.info("Showing districts with the highest increase in registered users from Q4 2022 to Q1 2023.")
    # CORRECTED QUERY
    query = """
    WITH q4_2022 AS (
        SELECT district_name, registered_users as users_q4_22 FROM map_user WHERE year = 2022 AND quarter = 4
    ),
    q1_2023 AS (
        SELECT district_name, registered_users as users_q1_23 FROM map_user WHERE year = 2023 AND quarter = 1
    )
    SELECT
        q1.district_name,
        (q1.users_q1_23 - q4.users_q4_22) as new_registrations
    FROM q1_2023 q1
    JOIN q4_2022 q4 ON q1.district_name = q4.district_name
    WHERE (q1.users_q1_23 - q4.users_q4_22) > 0
    ORDER BY new_registrations DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        fig = px.bar(
            df,
            x='district_name',
            y='new_registrations',
            title='Top District Contributors to User Growth (Q1 2023)',
            labels={'district_name': 'District', 'new_registrations': 'New Registered Users'},
            color='new_registrations',
            color_continuous_scale='Inferno'
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Main function to display Scenario 6 ---
def show_scenario_6():
    st.header("🔹 Scenario 6: User Registration Analysis")
    st.markdown("Analyze where and when most users register, down to the district level.")
    
    question = st.selectbox("Choose a question to analyze:", [
        "Which states have the highest number of registered users in 2022 Q3?",
        "What is the trend of user registrations across all quarters since 2018?",
        "Which pin codes had the highest registrations overall?",
        "How many new users registered in each state per quarter during 2021?",
        "Which districts contributed the most to registrations in early 2023?",
    ], key='scenario6_selectbox')
    st.markdown("---")

    if "2022 Q3" in question:
        question_1_top_states_2022_q3()
    elif "trend of user registrations" in question:
        question_2_registration_trend_since_2018()
    elif "pin codes" in question:
        question_3_top_pincodes_by_registration()
    elif "during 2021" in question:
        question_4_new_users_by_region_2021()
    elif "early 2023" in question:
        question_5_district_contribution_early_2023()