# pages/3_Scenarios.py
import streamlit as st
from scenario_1 import show_scenario_1
from scenario_2 import show_scenario_2
from scenario_3 import show_scenario_3
from scenario_4 import show_scenario_4
from scenario_5 import show_scenario_5
from scenario_6 import show_scenario_6 # <-- Import the final scenario function

st.set_page_config(layout="wide")
st.title("📊 Business Scenarios")

# --- Use tabs for different scenarios ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Scenario 1: Transactions",
    "Scenario 2: Market Expansion",
    "Scenario 3: States & Districts",
    "Scenario 4: Insurance",
    "Scenario 5: User Engagement",
    "Scenario 6: Registration Analysis" # <-- Updated tab name
])

with tab1:
    show_scenario_1()

with tab2:
    show_scenario_2()

with tab3:
    show_scenario_3()

with tab4:
    show_scenario_4()

with tab5:
    show_scenario_5()
    
with tab6:
    # This will display all the content from your final scenario
    show_scenario_6()