import streamlit as st

# Page config
st.set_page_config(page_title="PhonePe Transaction Insights - Project Overview", layout="wide")

# Title
st.title("📊 PhonePe Transaction Insights - Project Overview")

# Domain Introduction
st.header("Domain Introduction")
st.write("""
The project falls under the **Financial Technology (FinTech)** and **Digital Payments** domain, 
focusing on Unified Payments Interface (UPI) transaction data.  
It explores nationwide payment patterns to derive actionable business insights.
""")

# Project Introduction
st.header("Project Introduction")
st.write("""
Developed an interactive dashboard inspired by **PhonePe Pulse** to visualize  
UPI transactions at national, state, and district levels.
""")

# Objective
st.header("Objective")
st.write("""
To analyze transaction volumes, user adoption, and insurance patterns  
in order to identify growth opportunities and optimize payment strategies.
""")

# ELT Approach
st.header("ELT Approach")
st.markdown("""
- **Extract:** Pulled raw JSON data from the PhonePe Pulse GitHub repository.  
- **Load:** Stored structured data into **PostgreSQL** tables for optimized querying.  
- **Transform:** Cleaned, formatted, and enriched data (e.g., Indian currency formatting) for analysis.
""")

# Data Migration
st.header("Data Migration")
st.write("""
Data extracted from raw JSON files (simulating unstructured sources like MongoDB)  
was transformed into tabular form and loaded into **PostgreSQL** for analytical processing.
""")

# EDA Findings
st.header("Exploratory Data Analysis (EDA) Findings")
st.markdown("""
- Maharashtra, Karnataka, and Tamil Nadu lead in transaction amounts.  
- Q4 consistently shows higher transaction volumes due to seasonal spikes.  
- Insurance adoption shows steady growth but is concentrated in metro areas.
""")

# Feature Engineering
st.header("Feature Engineering")
st.write("""
- Created **transaction density** metric combining count and amount per state.  
- Generated quarter-based temporal features for trend analysis.
""")

# Statistical Techniques
st.header("Statistical Techniques")
st.write("""
Applied **Pearson Correlation** to measure the relationship between transaction count  
and amount, confirming a strong positive correlation.
""")

# Conclusion
st.header("Conclusion")
st.write("""
UPI transactions are rapidly scaling, with urban dominance but growing rural penetration.  
Insurance products are an emerging cross-sell opportunity.
""")

# Business Suggestions
st.header("Business Suggestions")
st.markdown("""
- Focus marketing campaigns during **Q4** to leverage seasonal transaction peaks.  
- Introduce localized insurance offerings in **tier-2 and tier-3 cities** to tap into untapped markets.
""")
