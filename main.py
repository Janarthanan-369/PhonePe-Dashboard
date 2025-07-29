'''phone pe pulse's data insights project'''

import streamlit as st

# === 🏠 Set Page Config ===
st.set_page_config(
    page_title="PhonePe Transaction Insights",
    page_icon="📊",
    layout="wide",
)

# === 🧾 Main Landing Page ===

import streamlit as st

# === Page Routing with Navigation API ===

import streamlit as st

pages = {
    "📁 PhonePe Dashboard": [
        st.Page("pages/1_About_Project.py", title="📄 About PhonePe Project"),
        st.Page("pages/2_India_Map.py", title="🗺️ India Map Insights"),
        st.Page("pages/3_Scenarios.py", title="📊 Business Scenarios"),
        st.Page("pages/4_Custom_Analysis.py", title="🔍 Custom Analysis"),
    ]
}

pg = st.navigation(pages)
pg.run()

