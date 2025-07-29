# pages/3_Scenarios.py

import streamlit as st
from utils.db_connection import run_query

st.title("📊 Scenario-Based Analysis")

# Scenario 1: Top States by Transaction Count (Sample)
st.header("Scenario 1: Decoding Transaction Dynamics")

query = """
SELECT 
    state, 
    SUM(txn_amount) AS total_transaction_value
FROM aggregated_transactions
WHERE year IN (2023, 2024) AND quarter IN (1, 2, 3, 4)
GROUP BY state
ORDER BY total_transaction_value DESC;
"""

df = run_query(query)

st.write("### 🔝 Top 10 States by Transaction Count (Q4 2023)")
st.dataframe(df)

# Optional: Visualization
st.bar_chart(df.set_index("state"))
