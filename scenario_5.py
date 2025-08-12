# scenario_5.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import run_query

# --- Functions for each question ---

def question_1_engagement_by_state():
    """Q1: Which states have the highest number of app opens per registered user?"""
    st.subheader("Top 10 States by User Engagement (App Opens per User)")
    st.info("This metric is calculated by dividing the total app opens by the latest registered user count for each state.")
    query = """
    WITH state_data AS (
        SELECT
            state,
            SUM(app_opens) as total_app_opens,
            MAX(CASE
                WHEN (year * 10 + quarter) = (SELECT MAX(year * 10 + quarter) FROM aggregated_user)
                THEN registered_users
                ELSE 0
            END) as latest_registered_users
        FROM aggregated_user
        WHERE device_brand IS NULL OR device_brand = ''
        GROUP BY state
    )
    SELECT
        state,
        CASE
            WHEN latest_registered_users > 0 THEN total_app_opens::float / latest_registered_users
            ELSE 0
        END as opens_per_user
    FROM state_data
    WHERE latest_registered_users > 0
    ORDER BY opens_per_user DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        fig = px.bar(
            df,
            x='state',
            y='opens_per_user',
            title="Highest User Engagement by State",
            labels={'state': 'State', 'opens_per_user': 'App Opens per Registered User'},
            color='opens_per_user',
            color_continuous_scale=px.colors.sequential.Cividis_r
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_2_peak_user_growth_quarter():
    """Q2: In which quarter did PhonePe see the largest increase in registered users nationwide?"""
    st.subheader("Quarter with Largest Increase in Registered Users")
    query = """
    WITH quarterly_users AS (
        SELECT year, quarter, SUM(registered_users) as total_users
        FROM aggregated_user
        WHERE device_brand IS NULL OR device_brand = ''
        GROUP BY year, quarter
    ),
    user_growth AS (
        SELECT
            CONCAT(year, '-Q', quarter) as period,
            total_users,
            LAG(total_users, 1, 0) OVER (ORDER BY year, quarter) as previous_quarter_users
        FROM quarterly_users
    )
    SELECT
        period,
        (total_users - previous_quarter_users) as user_increase
    FROM user_growth
    WHERE previous_quarter_users > 0;
    """
    try:
        df = run_query(query)
        if not df.empty:
            peak_growth_df = df.loc[df['user_increase'].idxmax()]
            st.metric(
                label="Peak Growth Quarter",
                value=str(peak_growth_df['period']),
                delta=f"{peak_growth_df['user_increase']:,.0f} new users"
            )

            fig = px.bar(
                df, x='period', y='user_increase',
                title='Quarter-over-Quarter Increase in Registered Users',
                labels={'period': 'Quarter', 'user_increase': 'New Registered Users'}
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_3_lowest_engagement_states():
    """Q3: Which 3 states had the lowest user engagement (app opens vs registrations)?"""
    st.subheader("Bottom 3 States by User Engagement")
    st.info("Showing states with the lowest ratio of total app opens to latest registered users (minimum 1,000 users).")
    query = """
    WITH state_data AS (
        SELECT
            state,
            SUM(app_opens) as total_app_opens,
            MAX(CASE
                WHEN (year * 10 + quarter) = (SELECT MAX(year * 10 + quarter) FROM aggregated_user)
                THEN registered_users
                ELSE 0
            END) as latest_registered_users
        FROM aggregated_user
        WHERE device_brand IS NULL OR device_brand = ''
        GROUP BY state
    )
    SELECT
        state,
        CASE
            WHEN latest_registered_users > 0 THEN total_app_opens::float / latest_registered_users
            ELSE 0
        END as opens_per_user
    FROM state_data
    WHERE latest_registered_users > 1000 -- Filter out very small states
    ORDER BY opens_per_user ASC
    LIMIT 3;
    """
    try:
        df = run_query(query)
        st.dataframe(df.style.format({'opens_per_user': '{:.2f}'}), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_4_engagement_ratio_over_time():
    """Q4: How does the ratio of registered users to app opens vary across time?"""
    st.subheader("User Engagement Ratio Over Time (Nationwide)")
    query = """
    SELECT
        CONCAT(year, '-Q', quarter) as period,
        CASE
            WHEN SUM(registered_users) > 0 THEN SUM(app_opens)::float / SUM(registered_users)
            ELSE 0
        END as engagement_ratio
    FROM aggregated_user
    WHERE device_brand IS NULL OR device_brand = ''
    GROUP BY year, quarter
    ORDER BY year, quarter;
    """
    try:
        df = run_query(query)
        fig = px.line(
            df, x='period', y='engagement_ratio',
            title='App Opens per Registered User Over Time',
            labels={'period': 'Quarter', 'engagement_ratio': 'Engagement Ratio'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info("This chart shows the average number of times the app was opened per registered user in each quarter.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_5_district_engagement_2022():
    """Q5: Which districts had the highest user engagement rate in 2022?"""
    st.subheader("Top 10 Districts by User Engagement in 2022")
    st.info("Engagement is calculated as total app opens in 2022 divided by registered users at the end of the year (Q4 2022).")
    query = """
    SELECT
        district_name,
        state_name,
        CASE
            WHEN MAX(CASE WHEN quarter = 4 THEN registered_user ELSE 0 END) > 0
            THEN SUM(app_opens)::float / MAX(CASE WHEN quarter = 4 THEN registered_user ELSE 0 END)
            ELSE 0
        END as engagement_rate
    FROM map_user
    WHERE year = 2022
    GROUP BY district_name, state_name
    HAVING MAX(CASE WHEN quarter = 4 THEN registered_user ELSE 0 END) > 1000
    ORDER BY engagement_rate DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        fig = px.bar(
            df, x='district_name', y='engagement_rate',
            title='Highest User Engagement by District (2022)',
            labels={'district_name': 'District', 'engagement_rate': 'App Opens per User'},
            color='engagement_rate', color_continuous_scale='Magma'
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Main function to display Scenario 5 ---
def show_scenario_5():
    st.header("🔹 Scenario 5: User Engagement and Growth Strategy")
    st.markdown("Analyze app opens and registered users to guide engagement improvements.")
    
    question = st.selectbox("Choose a question to analyze:", [
        "Which states have the highest number of app opens per registered user?",
        "In which quarter did PhonePe see the largest increase in registered users?",
        "Which 3 states had the lowest user engagement?",
        "How does the ratio of app opens to registered users vary across time?",
        "Which districts had the highest user engagement rate in 2022?",
    ], key='scenario5_selectbox')
    st.markdown("---")

    if "highest number of app opens" in question:
        question_1_engagement_by_state()
    elif "largest increase" in question:
        question_2_peak_user_growth_quarter()
    elif "lowest user engagement" in question:
        question_3_lowest_engagement_states()
    elif "vary across time" in question:
        question_4_engagement_ratio_over_time()
    elif "districts had the highest" in question:
        question_5_district_engagement_2022()