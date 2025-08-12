# scenario_4.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import run_query

# Re-using this helper function
def format_number(num):
    """Formats a number into a string with 'Cr' or 'Lakhs'."""
    if num >= 10000000:
        return f'₹{num / 10000000:.2f} Cr'
    elif num >= 100000:
        return f'₹{num / 100000:.2f} Lakhs'
    else:
        return f'₹{num:,.2f}'

# --- Functions for each question ---

def question_1_top_insurance_states():
    """Q1: Which states have the highest insurance transaction value in the most recent year?"""
    st.subheader("Top 10 States by Insurance Premium Value (Latest Year)")
    query = """
    WITH latest_year AS (
        SELECT MAX(year) as max_year FROM aggregated_insurance
    )
    SELECT
        state,
        SUM(amount) as total_insurance_value
    FROM aggregated_insurance
    WHERE year = (SELECT max_year FROM latest_year)
    GROUP BY state
    ORDER BY total_insurance_value DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        latest_year = run_query("SELECT MAX(year) as max_year FROM aggregated_insurance")['max_year'].iloc[0]
        st.info(f"Displaying data for the latest full year available: **{latest_year}**")

        df['formatted_value'] = df['total_insurance_value'].apply(format_number)
        fig = px.bar(
            df,
            x='state',
            y='total_insurance_value',
            title=f"Highest Insurance Premium Value by State in {latest_year}",
            labels={'state': 'State', 'total_insurance_value': 'Total Premium Value'},
            hover_data={'formatted_value': True, 'total_insurance_value': False},
            color='total_insurance_value',
            color_continuous_scale=px.colors.sequential.PuBu
        )
        fig.update_traces(hovertemplate='<b>%{x}</b><br>Premium Value: %{customdata[0]}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_2_insurance_trend():
    """Q2: What is the trend in insurance transaction value across years from 2020 to 2023?"""
    st.subheader("Trend of Insurance Premium Value (2020-2023)")
    query = """
    SELECT
        year,
        SUM(amount) as total_insurance_value
    FROM aggregated_insurance
    WHERE year BETWEEN 2020 AND 2023
    GROUP BY year
    ORDER BY year;
    """
    try:
        df = run_query(query)
        df['formatted_value'] = df['total_insurance_value'].apply(format_number)
        fig = px.line(
            df,
            x='year',
            y='total_insurance_value',
            title='Total Insurance Premium Value Over Time',
            labels={'year': 'Year', 'total_insurance_value': 'Total Premium Value'},
            markers=True,
            custom_data=['formatted_value']
        )
        fig.update_traces(hovertemplate='<b>Year %{x}</b><br>Premium Value: %{customdata[0]}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_3_underserved_states():
    """Q3: Which states have zero or minimal insurance adoption despite high transaction activity?"""
    st.subheader("Opportunity Analysis: High Transaction Volume vs. Low Insurance Adoption")
    query = """
    WITH insurance_summary AS (
        SELECT state, SUM(amount) as total_insurance_value
        FROM aggregated_insurance GROUP BY state
    ),
    transaction_summary AS (
        SELECT state, SUM(txn_count) as total_transaction_count
        FROM aggregated_transactions GROUP BY state
    )
    SELECT
        ts.state,
        ts.total_transaction_count,
        COALESCE(ins.total_insurance_value, 0) as total_insurance_value
    FROM transaction_summary ts
    LEFT JOIN insurance_summary ins ON ts.state = ins.state;
    """
    try:
        df = run_query(query)
        fig = px.scatter(
            df,
            x='total_transaction_count',
            y='total_insurance_value',
            text='state',
            title='Transaction Volume vs. Insurance Premium Value',
            labels={'total_transaction_count': 'Total Transaction Count (Log Scale)', 'total_insurance_value': 'Total Insurance Value (Log Scale)'},
            log_x=True, log_y=True
        )
        fig.update_traces(textposition='top center', textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            """
            **How to interpret this chart:**
            States in the **bottom-right quadrant** have high overall transaction activity but low insurance premiums collected.
            These represent potential high-priority markets for insurance expansion.
            """
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_4_avg_value_per_user():
    """Q4: What is the average insurance transaction value per user in each state?"""
    st.subheader("Average Insurance Premium Value per Registered User")
    st.warning("**Note:** This analysis relies on the latest registered user count for each state. The `aggregated_user` table structure is assumed to contain overall user counts in rows where `device_brand` is not specified.")
    query = """
    WITH total_insurance AS (
        SELECT state, SUM(amount) as total_insurance_value
        FROM aggregated_insurance GROUP BY state
    ),
    latest_users AS (
        SELECT state, registered_users
        FROM (
            SELECT state, registered_users,
                   ROW_NUMBER() OVER(PARTITION BY state ORDER BY year DESC, quarter DESC) as rn
            FROM aggregated_user
            WHERE device_brand IS NULL OR device_brand = ''
        ) as ranked_users
        WHERE rn = 1
    )
    SELECT
        lu.state,
        ti.total_insurance_value,
        lu.registered_users,
        CASE
            WHEN lu.registered_users > 0 THEN ti.total_insurance_value / lu.registered_users
            ELSE 0
        END as avg_value_per_user
    FROM latest_users lu
    JOIN total_insurance ti ON lu.state = ti.state
    WHERE lu.registered_users > 0
    ORDER BY avg_value_per_user DESC;
    """
    try:
        df = run_query(query)
        fig = px.bar(
            df,
            x='state',
            y='avg_value_per_user',
            title='Average Insurance Premium per User by State',
            labels={'state': 'State', 'avg_value_per_user': 'Average Premium per User (₹)'},
            color='avg_value_per_user',
            color_continuous_scale=px.colors.sequential.Sunset
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_5_peak_insurance_quarter():
    """Q5: Which quarter had the highest spike in insurance adoption across India?"""
    st.subheader("Peak Quarter for Insurance Policy Sales")
    query = """
    SELECT
        CONCAT(year, '-Q', quarter) as period,
        SUM(transaction_count) as total_insurance_policies
    FROM aggregated_insurance
    GROUP BY year, quarter
    ORDER BY year, quarter;
    """
    try:
        df = run_query(query)
        if not df.empty:
            peak_period_df = df.loc[df['total_insurance_policies'].idxmax()]
            st.metric(
                label="Highest Sales Quarter",
                value=str(peak_period_df['period']),
                delta=f"{peak_period_df['total_insurance_policies']:,} policies sold"
            )
            fig = px.line(
                df, x='period', y='total_insurance_policies',
                title='Total Insurance Policies Sold per Quarter',
                labels={'period': 'Quarter', 'total_insurance_policies': 'Number of Policies Sold'},
                markers=True
            )
            # Add a vertical line to highlight the peak
            fig.add_vline(x=peak_period_df['period'], line_width=3, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Main function to display Scenario 4 ---
def show_scenario_4():
    st.header("🔹 Scenario 4: Insurance Penetration and Growth")
    st.markdown("Analyze insurance transaction growth and identify underserved states.")
    
    question = st.selectbox("Choose a question to analyze:", [
        "Which states have the highest insurance transaction value in the most recent year?",
        "What is the trend in insurance transaction value across years from 2020 to 2023?",
        "Which states have minimal insurance adoption despite high transaction activity?",
        "What is the average insurance transaction value per user in each state?",
        "Which quarter had the highest spike in insurance adoption across India?",
    ], key='scenario4_selectbox')
    st.markdown("---")

    if "most recent year" in question:
        question_1_top_insurance_states()
    elif "trend in insurance" in question:
        question_2_insurance_trend()
    elif "minimal insurance adoption" in question:
        question_3_underserved_states()
    elif "average insurance transaction value" in question:
        question_4_avg_value_per_user()
    elif "highest spike" in question:
        question_5_peak_insurance_quarter()