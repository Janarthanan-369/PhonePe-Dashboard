import streamlit as st

def app():
    st.title("📌 Project Overview")
    
    st.markdown("""
    ### 1. **Data Extraction & Transformation**
    - Cloned and structured JSON files from PhonePe Pulse into CSV format.
    
    ### 2. **Database Integration**
    - Designed a PostgreSQL schema and inserted processed data using **SQLAlchemy** for cleaner and modular code.
    
    ### 3. **Dashboard Development**
    - Built with **Streamlit**, enabling interactive filtering by state, year, and quarter, plus hover tooltips with **Indian number formatting**.
    
    ### 4. **Visualization & Insights**
    - Created **6 business scenarios** with **5 charts each** (total **30 charts**) covering transactions, users, insurance, top categories, and geo-based insights.
    
    ### 5. **Custom Analysis**
    - Added unique interpretations beyond PhonePe’s own reports to highlight market trends and patterns.
    """)

    st.subheader("💻 Tech Stack")
    st.markdown("`Python` • `Pandas` • `SQLAlchemy` • `PostgreSQL` • `Streamlit` • `PyDeck` • `Git` • `JSON to CSV conversion` • `Data Cleaning & Transformation`")

    st.subheader("🔍 Highlights")
    st.markdown("""
    - **Fully automated ETL pipeline** from JSON to PostgreSQL  
    - **Map-based visualizations** replicating PhonePe’s 3D tower style  
    - **Modular code structure** for reusability and maintenance
    """)

# If running this page directly
if __name__ == "__main__":
    app()
