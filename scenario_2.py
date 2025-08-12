# scenario_2.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import run_query

# --- Functions for each question ---

def question_1_district_growth():
    """Q1: Which districts have shown the highest growth in transaction value in the last 4 quarters?"""
    st.subheader("Top 10 Districts by Transaction Value Growth (Last 4 Quarters)")
    # This query finds the latest period, the period 4 quarters prior, and calculates the growth between them.
    query = """
    WITH quarterly_data AS (
        SELECT
            state_name,
            district_name,
            year,
            quarter,
            SUM(amount) as total_amount,
            -- Create a single sortable period identifier
            (year * 10 + quarter) as period_id
        FROM map_transaction_hover
        GROUP BY state_name, district_name, year, quarter
    ),
    distinct_periods AS (
        -- Get the last 5 distinct periods available in the data
        SELECT DISTINCT period_id FROM quarterly_data ORDER BY period_id DESC LIMIT 5
    ),
    latest_period AS (
        -- The most recent period
        SELECT period_id FROM distinct_periods ORDER BY period_id DESC LIMIT 1
    ),
    prior_period AS (
        -- The period 4 quarters ago (5th one from the end)
        SELECT period_id FROM distinct_periods ORDER BY period_id ASC LIMIT 1
    ),
    latest_values AS (
        SELECT district_name, total_amount as latest_amount
        FROM quarterly_data WHERE period_id = (SELECT period_id FROM latest_period)
    ),
    prior_values AS (
        SELECT district_name, total_amount as prior_amount
        FROM quarterly_data WHERE period_id = (SELECT period_id FROM prior_period)
    )
    SELECT
        l.district_name,
        p.prior_amount,
        l.latest_amount,
        ((l.latest_amount - p.prior_amount) * 100.0 / p.prior_amount) as growth_percentage
    FROM latest_values l
    JOIN prior_values p ON l.district_name = p.district_name
    WHERE p.prior_amount > 0 -- Avoid division by zero and districts with no prior data
    ORDER BY growth_percentage DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        if not df.empty:
            fig = px.bar(
                df,
                x='district_name',
                y='growth_percentage',
                title="Highest Growth Districts",
                labels={'district_name': 'District', 'growth_percentage': 'Growth (%)'},
                color='growth_percentage',
                color_continuous_scale=px.colors.sequential.YlGn
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("This chart displays the top 10 districts with the highest percentage growth in total transaction value when comparing the most recent quarter to the same quarter of the previous year.")
        else:
            st.warning("Could not compute district growth. This may be due to insufficient data across the required time periods.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_2_low_avg_txn_size():
    """Q2: Which regions have high transaction volume but low transaction value (low avg txn size)?"""
    st.subheader("Analysis of Transaction Volume vs. Average Transaction Value")
    query = """
    SELECT
        district_name,
        state_name,
        SUM(transaction_count) as total_volume,
        SUM(amount) / SUM(transaction_count) as avg_txn_size
    FROM map_transaction_hover
    WHERE transaction_count > 0 AND amount > 0 -- Ensure valid calculations
    GROUP BY district_name, state_name;
    """
    try:
        df = run_query(query)
        fig = px.scatter(
            df,
            x='total_volume',
            y='avg_txn_size',
            color='state_name',
            hover_name='district_name',
            title='District-wise Transaction Volume vs. Average Value',
            labels={'total_volume': 'Total Transaction Count (Volume)', 'avg_txn_size': 'Average Transaction Value (₹)'},
            log_x=True, # Use a log scale for better visualization of volume
            log_y=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            """
            **How to interpret this chart:**
            - **Bottom-Right Quadrant**: Districts here have high transaction volume but a low average value per transaction. These are potential markets for micro-transactions, digital payments for small-value items, and peer-to-peer transfers.
            - **Top-Left Quadrant**: Districts here have low volume but high-value transactions.
            """
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_3_top_districts_2023():
    """Q3: List the top 10 districts with the most transaction activity in 2023."""
    st.subheader("Top 10 Districts by Transaction Count in 2023")
    st.warning("**Note:** Pincode-level transaction data is not available in the provided tables. This analysis has been performed at the **district level** instead.")
    query = """
    SELECT
        district_name,
        state_name,
        SUM(transaction_count) as total_transactions
    FROM top_transaction -- This table is suitable for district-level top analysis
    WHERE year = 2023
    GROUP BY district_name, state_name
    ORDER BY total_transactions DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_4_bottom_states():
    """Q4: Which states consistently rank in the bottom 5 for transaction activity?"""
    st.subheader("States Consistently in Bottom 5 for Transaction Count")
    query = """
    WITH ranked_states AS (
        SELECT
            state,
            year,
            quarter,
            SUM(txn_count) as total_transactions,
            -- Rank states within each period, 1 being the lowest
            RANK() OVER(PARTITION BY year, quarter ORDER BY SUM(txn_count) ASC) as rnk
        FROM aggregated_transactions
        GROUP BY state, year, quarter
    )
    SELECT
        state,
        COUNT(*) as times_in_bottom_5
    FROM ranked_states
    WHERE rnk <= 5
    GROUP BY state
    ORDER BY times_in_bottom_5 DESC;
    """
    try:
        df = run_query(query)
        fig = px.bar(
            df,
            x='state',
            y='times_in_bottom_5',
            title="Frequency of Appearing in Bottom 5 States by Transaction Count",
            labels={'state': 'State', 'times_in_bottom_5': 'Number of Quarters in Bottom 5'},
            color_discrete_sequence=['#d62728']
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info("This chart identifies states that have most frequently ranked in the bottom 5 for total transaction count per quarter, indicating lower digital payment adoption or activity.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_5_cagr_analysis():
    """Q5: What is the CAGR of total transactions in top 5 states since 2018?"""
    st.subheader("Transaction CAGR for Top 5 States (2018-Present)")
    # This complex query identifies the top 5 states, finds their first and last year transaction counts,
    # and then calculates the Compound Annual Growth Rate (CAGR).
    query = """
    WITH top_states AS (
        SELECT state
        FROM aggregated_transactions
        WHERE year >= 2018
        GROUP BY state
        ORDER BY SUM(txn_count) DESC
        LIMIT 5
    ),
    yearly_data AS (
        SELECT
            state,
            year,
            SUM(txn_count) as total_count
        FROM aggregated_transactions
        WHERE state IN (SELECT state FROM top_states) AND year >= 2018
        GROUP BY state, year
    ),
    start_end_values AS (
        SELECT
            state,
            -- Get the transaction count from the first year
            FIRST_VALUE(total_count) OVER(PARTITION BY state ORDER BY year ASC) as start_value,
            -- Get the transaction count from the last year
            LAST_VALUE(total_count) OVER(PARTITION BY state ORDER BY year ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as end_value,
            -- Get the first year
            FIRST_VALUE(year) OVER(PARTITION BY state ORDER BY year ASC) as start_year,
            -- Get the last year
            LAST_VALUE(year) OVER(PARTITION BY state ORDER BY year ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as end_year
        FROM yearly_data
    ),
    distinct_cagr AS (
        SELECT DISTINCT
            state,
            start_value,
            end_value,
            start_year,
            end_year,
            -- Calculate number of periods (years)
            (end_year - start_year) as num_years
        FROM start_end_values
    )
    SELECT
        state,
        -- Calculate CAGR: ((End/Start)^(1/N)) - 1
        (POW((end_value::numeric / start_value), (1.0 / num_years)) - 1) * 100 as cagr_percentage
    FROM distinct_cagr
    WHERE num_years > 0 AND start_value > 0;
    """
    try:
        df = run_query(query)
        df['cagr_percentage'] = df['cagr_percentage'].astype(float).round(2)
        fig = px.bar(
            df,
            x='state',
            y='cagr_percentage',
            title="Compound Annual Growth Rate (CAGR) of Transactions",
            labels={'state': 'State', 'cagr_percentage': 'CAGR (%)'},
            color='cagr_percentage',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info("CAGR represents the mean annual growth rate of transactions over a specified period of time, smoothing out volatility.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Main function to display Scenario 2 ---
def show_scenario_2():
    st.header("🔹 Scenario 2: Transaction Analysis for Market Expansion")
    st.markdown("""
    Identify trends and opportunities for expansion based on transaction data.
    Select a question from the dropdown below to see the analysis.
    """)
    question = st.selectbox("Choose a question to analyze:", [
        "Which districts have shown the highest growth in transaction value in the last 4 quarters?",
        "Which regions have high transaction volume but low transaction value (low avg txn size)?",
        "List the top 10 districts with the most transaction activity in 2023.",
        "Which states consistently rank in the bottom 5 for transaction activity?",
        "What is the CAGR of total transactions in top 5 states since 2018?",
    ], key='scenario2_selectbox') # Add a unique key
    st.markdown("---")

    if question == "Which districts have shown the highest growth in transaction value in the last 4 quarters?":
        question_1_district_growth()
    elif question == "Which regions have high transaction volume but low transaction value (low avg txn size)?":
        question_2_low_avg_txn_size()
    elif question == "List the top 10 districts with the most transaction activity in 2023.":
        question_3_top_districts_2023()
    elif question == "Which states consistently rank in the bottom 5 for transaction activity?":
        question_4_bottom_states()
    elif question == "What is the CAGR of total transactions in top 5 states since 2018?":
        question_5_cagr_analysis()