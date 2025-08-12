# scenario_3.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import run_query

# Utility function from Scenario 1, good to have here as well
def format_number(num):
    """Formats a number into a string with 'Cr' or 'Lakhs'."""
    if num >= 10000000:
        return f'₹{num / 10000000:.2f} Cr'
    elif num >= 100000:
        return f'₹{num / 100000:.2f} Lakhs'
    else:
        return f'₹{num:,.2f}'

# --- Functions for each question ---

def question_1_top_districts_q4_2022():
    """Q1: Which 10 districts recorded the highest transaction value in Q4 2022?"""
    st.subheader("Top 10 Districts by Transaction Value (Q4 2022)")
    query = """
    SELECT
        district_name,
        state_name,
        SUM(amount) as total_value
    FROM map_transaction_hover
    WHERE year = 2022 AND quarter = 4
    GROUP BY district_name, state_name
    ORDER BY total_value DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        df['formatted_value'] = df['total_value'].apply(format_number)
        fig = px.bar(
            df,
            y='district_name',
            x='total_value',
            orientation='h',
            title="Highest Transaction Value Districts in Q4 2022",
            labels={'district_name': 'District', 'total_value': 'Total Transaction Value'},
            hover_data={'formatted_value': True, 'total_value': False},
            color='total_value',
            color_continuous_scale=px.colors.sequential.algae
        )
        fig.update_traces(hovertemplate='<b>%{y}</b><br>Transaction Value: %{customdata[0]}<extra></extra>')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_2_state_domination_pincodes():
    """Q2: Which states dominate the top 100 pin codes by transaction count?"""
    st.subheader("State-wise Distribution of Top 100 Pincodes")
    st.warning("**Note:** Pincode-level **transaction** data is not available. This analysis uses **registered user** data from the `top_user_by_pincode` table as a proxy for activity.")
    query = """
    WITH top_100_pincodes AS (
        SELECT state, pincode, registeredusers
        FROM top_user_by_pincode
        ORDER BY registeredusers DESC
        LIMIT 100
    )
    SELECT
        state,
        COUNT(pincode) as pincode_count
    FROM top_100_pincodes
    GROUP BY state
    ORDER BY pincode_count DESC;
    """
    try:
        df = run_query(query)
        fig = px.treemap(
            df,
            path=[px.Constant("All States"), 'state'],
            values='pincode_count',
            title='Number of Top 100 Pincodes per State',
            color='pincode_count',
            color_continuous_scale='viridis'
        )
        fig.update_traces(textinfo='label+value', hovertemplate='<b>%{label}</b><br>Pincode Count: %{value}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
        st.info("This treemap shows which states contain the highest number of top-performing pincodes, based on registered user counts.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_3_top_5_states_contribution():
    """Q3: What percentage of total transaction value comes from the top 5 states?"""
    st.subheader("Contribution of Top 5 States to Total Transaction Value")
    query = """
    WITH state_totals AS (
        SELECT state, SUM(txn_amount) as total_amount
        FROM aggregated_transactions
        GROUP BY state
    ),
    top_5_total AS (
        SELECT SUM(total_amount) as top_5_sum
        FROM (SELECT total_amount FROM state_totals ORDER BY total_amount DESC LIMIT 5) as top_5
    ),
    overall_total AS (
        SELECT SUM(total_amount) as grand_total FROM state_totals
    )
    SELECT
        (SELECT top_5_sum FROM top_5_total) as top_5_contribution,
        (SELECT grand_total FROM overall_total) as total_contribution;
    """
    try:
        df = run_query(query)
        if not df.empty:
            top_5_val = df['top_5_contribution'].iloc[0]
            total_val = df['total_contribution'].iloc[0]
            percentage = (top_5_val / total_val) * 100
            rest_of_india_val = total_val - top_5_val

            st.metric(
                label="Percentage from Top 5 States",
                value=f"{percentage:.2f}%",
                help=f"The top 5 states contribute {format_number(top_5_val)} out of a total of {format_number(total_val)}."
            )

            pie_df = pd.DataFrame({
                'Category': ['Top 5 States', 'Rest of India'],
                'Value': [top_5_val, rest_of_india_val]
            })
            fig = px.pie(pie_df, values='Value', names='Category', title='Transaction Value Distribution', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_4_fastest_growth_district_2023():
    """Q4: Which district had the fastest growth in transaction count in 2023?"""
    st.subheader("Fastest Growing Districts by Transaction Count in 2023")
    query = """
    WITH q1_data AS (
        SELECT district_name, SUM(transaction_count) as q1_count
        FROM map_transaction_hover WHERE year = 2023 AND quarter = 1 GROUP BY district_name
    ),
    q4_data AS (
        SELECT district_name, SUM(transaction_count) as q4_count
        FROM map_transaction_hover WHERE year = 2023 AND quarter = 4 GROUP BY district_name
    )
    SELECT
        q1.district_name,
        q1.q1_count,
        q4.q4_count,
        ((q4.q4_count - q1.q1_count) * 100.0 / q1.q1_count) as growth_percentage
    FROM q1_data q1
    JOIN q4_data q4 ON q1.district_name = q4.district_name
    WHERE q1.q1_count > 1000 -- Filter for districts with a meaningful base transaction count
    ORDER BY growth_percentage DESC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        if not df.empty:
            top_district = df.iloc[0]
            st.metric(
                label=f"Fastest Growing District in 2023",
                value=top_district['district_name'],
                delta=f"{top_district['growth_percentage']:.2f}% Growth (Q1 vs Q4)"
            )
            fig = px.bar(df, x='district_name', y='growth_percentage', title="Top 10 Fastest Growing Districts",
                         labels={'district_name': 'District', 'growth_percentage': 'Growth (%)'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not retrieve growth data for 2023.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def question_5_bottom_districts_latest_year():
    """Q5: What are the bottom 10 districts in terms of transaction activity for the current year?"""
    st.subheader("Bottom 10 Districts by Transaction Count (Latest Full Year)")
    query = """
    WITH latest_year AS (
        SELECT MAX(year) as max_year FROM map_transaction_hover
    )
    SELECT
        district_name,
        state_name,
        SUM(transaction_count) as total_transactions
    FROM map_transaction_hover
    WHERE year = (SELECT max_year FROM latest_year)
    GROUP BY district_name, state_name
    ORDER BY total_transactions ASC
    LIMIT 10;
    """
    try:
        df = run_query(query)
        latest_year = run_query("SELECT MAX(year) as max_year FROM map_transaction_hover")['max_year'].iloc[0]
        st.info(f"Displaying data for the latest full year available in the dataset: **{latest_year}**")
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")


# --- Main function to display Scenario 3 ---
def show_scenario_3():
    st.header("🔹 Scenario 3: Transaction Analysis Across States and Districts")
    st.markdown("Identify top-performing states/districts by transaction volume and value.")
    
    question = st.selectbox("Choose a question to analyze:", [
        "Which 10 districts recorded the highest transaction value in Q4 2022?",
        "Which states dominate the top 100 pin codes by registered users?",
        "What percentage of total transaction value comes from the top 5 states?",
        "Which district had the fastest growth in transaction count in 2023?",
        "What are the bottom 10 districts in terms of transaction activity for the latest year?",
    ], key='scenario3_selectbox')
    st.markdown("---")

    if "Q4 2022" in question:
        question_1_top_districts_q4_2022()
    elif "pin codes" in question:
        question_2_state_domination_pincodes()
    elif "top 5 states" in question:
        question_3_top_5_states_contribution()
    elif "fastest growth" in question:
        question_4_fastest_growth_district_2023()
    elif "bottom 10 districts" in question:
        question_5_bottom_districts_latest_year()