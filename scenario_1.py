# scenario_1.py

# Importing tools we need to make our app work
import streamlit as st          # For making the web app
import pandas as pd             # For working with tables of data
import plotly.express as px     # For making cool charts
from utils.db_connection import run_query # This helps us get data from our database

# This function makes big numbers easier to read (like turning 10000000 into "1 Cr")
def format_number(num):
    """Turns a big number into 'Cr' (crore) or 'Lakhs' so it's easy to understand."""
    if num >= 10000000:
        return f'₹ {num / 10000000:.2f} Cr'    # If number is 1 crore or more
    elif num >= 100000:
        return f'₹ {num / 100000:.2f} Lakhs'   # If number is 1 lakh or more
    else:
        return f'₹ {num:.2f}'                  # If number is less than 1 lakh

# --- These are the answers to each question we want to show on the app ---

# 1. Which states had the most money spent in the latest quarter?
def question_1_highest_value_states():
    st.subheader("Top 10 States by Transaction Value (Latest Quarter)")
    # This gets the latest quarter and finds the top 10 states with most money spent
    query = """
        WITH latest_period AS (
            SELECT year, quarter FROM aggregated_transactions ORDER BY year DESC, quarter DESC LIMIT 1
        )
        SELECT state, SUM(txn_amount) as total_amount
        FROM aggregated_transactions
        WHERE (year, quarter) IN (SELECT year, quarter FROM latest_period)
        GROUP BY state ORDER BY total_amount DESC LIMIT 10;
    """
    try:
        df = run_query(query) # Get the data from the database
        df['formatted_amount'] = df['total_amount'].apply(format_number) # Make numbers easy to read
        # Make a bar chart showing states and how much money was spent
        fig = px.bar(df, x='state', y='total_amount', title="Highest Transaction Value by State",
                     labels={'state': 'State', 'total_amount': 'Total Transaction Value'},
                     hover_data={'formatted_amount': True, 'total_amount': False},
                     color_discrete_sequence=px.colors.sequential.Viridis)
        fig.update_traces(hovertemplate='<b>%{x}</b><br>Transaction Value: %{customdata[0]}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
        st.info("This chart shows the top 10 states with the highest total value of transactions in the most recently recorded quarter.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# 2. What are the top 5 ways people pay (like shopping, bills) in the last 2 years?
def question_2_top_payment_categories():
    st.subheader("Top 5 Payment Categories by Transaction Count (Last 2 Years)")
    query = """
        SELECT category, SUM(txn_count) AS total_count
        FROM aggregated_transactions
        WHERE year >= (SELECT MAX(year) - 1 FROM aggregated_transactions)
        GROUP BY category ORDER BY total_count DESC LIMIT 5;
    """
    try:
        df = run_query(query) # Get the data
        # Make a pie chart showing which payment types are most popular
        fig = px.pie(df, names='category', values='total_count', title="Top 5 Payment Categories Distribution",
                     hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Transaction Count: %{value:,}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
        st.info("This chart illustrates the market share of the top 5 payment categories based on the total number of transactions over the last two full years.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# 3. Which state grew the fastest in number of payments from 2021 to 2022?
def question_3_yoy_growth():
    st.subheader("Top 10 States by Year-over-Year Growth in Transaction Count (2021 vs 2022)")
    query = """
        WITH yearly_counts AS (
            SELECT state, year, SUM(txn_count) as total_count FROM aggregated_transactions WHERE year IN (2021, 2022) GROUP BY state, year
        ), pivoted_counts AS (
            SELECT state, SUM(CASE WHEN year = 2021 THEN total_count ELSE 0 END) AS count_2021,
            SUM(CASE WHEN year = 2022 THEN total_count ELSE 0 END) AS count_2022 FROM yearly_counts GROUP BY state
        )
        SELECT state, count_2021, count_2022,
            CASE WHEN count_2021 > 0 THEN ((count_2022 - count_2021) * 100.0 / count_2021) ELSE 0 END AS yoy_growth_percentage
        FROM pivoted_counts WHERE count_2021 > 0 AND count_2022 > 0 ORDER BY yoy_growth_percentage DESC LIMIT 10;
    """
    try:
        df = run_query(query) # Get the data
        if not df.empty:
            top_state = df.iloc[0]
            # Show the state that grew the fastest
            st.metric(label=f"Top Growing State (2021-2022)", value=top_state['state'], delta=f"{top_state['yoy_growth_percentage']:.2f}%")
            # Make a bar chart showing growth for top 10 states
            fig = px.bar(df, x='state', y='yoy_growth_percentage', title="Top 10 States by YoY Transaction Count Growth",
                         labels={'state': 'State', 'yoy_growth_percentage': 'YoY Growth (%)'}, color='yoy_growth_percentage',
                         color_continuous_scale=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)
            st.info("This chart highlights the states that experienced the most significant percentage growth in transaction counts from 2021 to 2022.")
        else:
            st.warning("Could not retrieve data for the specified years (2021 and 2022).")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# 4. How does money spent change every quarter for the top 3 states?
def question_4_quarterly_variation():
    st.subheader("Quarterly Transaction Value for Top 3 States")
    try:
        # Find the top 3 states with most money spent
        top_states_query = "SELECT state FROM aggregated_transactions GROUP BY state ORDER BY SUM(txn_amount) DESC LIMIT 3;"
        top_states_df = run_query(top_states_query)
        top_states_list = top_states_df['state'].tolist()
        if top_states_list:
            states_tuple = tuple(top_states_list)
            # Get data for those states for every quarter
            quarterly_data_query = f"""
                SELECT CONCAT(year, '-Q', quarter) AS period, state, SUM(txn_amount) AS total_amount
                FROM aggregated_transactions WHERE state IN {states_tuple}
                GROUP BY state, year, quarter ORDER BY year, quarter, state;
            """
            df_quarterly = run_query(quarterly_data_query)
            # Make a line chart showing how money spent changes over time
            fig = px.line(df_quarterly, x='period', y='total_amount', color='state',
                          title="Quarter-over-Quarter Transaction Value", markers=True,
                          labels={'period': 'Quarter', 'total_amount': 'Total Transaction Value', 'state': 'State'})
            st.plotly_chart(fig, use_container_width=True)
            st.info("This line chart tracks the total transaction value over time for the three states with the highest overall transaction value.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# 5. Which quarters had the least number of payments since 2018?
def question_5_lowest_activity_quarters():
    st.subheader("Top 10 Quarters with Lowest Transaction Count (Since 2018)")
    query = """
        SELECT CONCAT(year, '-Q', quarter) AS period, SUM(txn_count) AS total_transactions
        FROM aggregated_transactions WHERE year >= 2018
        GROUP BY year, quarter ORDER BY total_transactions ASC LIMIT 10;
    """
    try:
        df = run_query(query)
        # Make a bar chart showing the quarters with the least payments
        fig = px.bar(df.sort_values(by='total_transactions'), x='period', y='total_transactions',
                     title="Lowest Transaction Activity by Quarter",
                     labels={'period': 'Period (Year-Quarter)', 'total_transactions': 'Total Transaction Count'},
                     color_discrete_sequence=['#ff6347'])
        st.plotly_chart(fig, use_container_width=True)
        st.info("This chart identifies the 10 quarters with the lowest overall transaction counts since 2018.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- This is the main part that shows everything on the app ---
def show_scenario_1():
    st.header("🔹 Scenario 1: Decoding Transaction Dynamics")
    st.markdown("""
    Analyse variations in transaction behaviour across states, quarters, and payment categories.
    Select a question from the dropdown below to see the analysis.
    """)
    # Let the user pick which question they want to see
    question = st.selectbox("Choose a question to analyze:", [
        "Which states had the highest total transaction value in the latest quarter?",
        "What are the top 5 payment categories by transaction count in the last two years?",
        "Which state saw the highest year-over-year growth in transaction count between 2021 and 2022?",
        "How does transaction value vary quarter-over-quarter for the top 3 performing states?",
        "Which quarters have seen the lowest overall transaction activity since 2018?"
    ])
    st.markdown("---")
    # Show the answer for the question the user picked
    if question == "Which states had the highest total transaction value in the latest quarter?":
        question_1_highest_value_states()
    elif question == "What are the top 5 payment categories by transaction count in the last two years?":
        question_2_top_payment_categories()
    elif question == "Which state saw the highest year-over-year growth in transaction count between 2021 and 2022?":
        question_3_yoy_growth()
    elif question == "How does transaction value vary quarter-over-quarter for the top 3 performing states?":
        question_4_quarterly_variation()
    elif question == "Which quarters have seen the lowest overall transaction activity since 2018?":
        question_5_lowest_activity_quarters()